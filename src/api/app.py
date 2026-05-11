from collections import deque
from datetime import datetime, timedelta

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.api_providers.common_df_merger.multiple_dataframe_transformer import Multiple_df_manager
from src.ml_work.feature_engineering.feature_engineering_regression_lgbm import (
    FeatureRegressionEngineeringLGBMR,
)
from src.pipeline.pipeline import DataPipeline
from src.pipeline.utils import SYMBOL_MAPPINGS

app = FastAPI(
    title="Gold Prediction API",
    description="API do predykcji kierunku złota za pomocą modelu LGBM",
    version="0.1.0",
)

# Model i feature_columns ładowane raz przy starcie serwera
try:
    model = joblib.load("models/lgbm_classifier.pkl")
    feature_columns = joblib.load("models/feature_columns.pkl")
except FileNotFoundError:
    raise RuntimeError("Nie znaleziono plików modelu. Uruchom najpierw pipeline treningowy.")


class PredictRequest(BaseModel):
    asset_name: str


class PredictResponse(BaseModel):
    prediction: str  # "long" lub "no_trade"
    probability: float  # pewność modelu (0.0 - 1.0)


# Cache w pamięci — dane rynkowe zmieniają się raz dziennie, nie ma sensu odpytywać API przy każdym requeście
_cache: dict = {"data": None, "expires_at": datetime.min}


def get_latest_features() -> pd.DataFrame:
    if _cache["data"] is not None and datetime.now() < _cache["expires_at"]:
        return _cache["data"]

    # Twelve Data: ceny rynkowe (ETF, surowce, krypto)
    twelve_symbols = deque(["GLD", "SPY", "USO", "BNO", "BTC/USD"])
    twelve_data = DataPipeline().run_requests(twelve_symbols, "twelve", SYMBOL_MAPPINGS, 200)

    # FRED: waluty, VIX, wskaźniki makro
    fred_symbols = deque(
        [
            "DEXUSEU",
            "DEXUSUK",
            "DEXSZUS",
            "DEXJPUS",
            "DEXSDUS",
            "DEXCAUS",
            "VIXCLS",
            "USEPUINDXD",
            "INFECTDISEMVTRACKD",
        ]
    )
    fred_data = DataPipeline().run_requests(fred_symbols, "fred", SYMBOL_MAPPINGS, 500)

    merged = Multiple_df_manager()
    merged.multiple_df_manager_pipeline(twelve_data)
    merged.multiple_df_manager_pipeline(fred_data)
    df_final = merged.return_df

    fe = FeatureRegressionEngineeringLGBMR()
    fe.feature_enginerring_pipeline(df_final)

    # Bierzemy ostatni kompletny wiersz (najnowszy dzień bez NaN)
    df_features = fe.return_dataframe.dropna()
    result = df_features[feature_columns].iloc[[-1]]

    _cache["data"] = result
    _cache["expires_at"] = datetime.now() + timedelta(hours=12)
    return result


# uruchomienie lokalne:
# source venv/bin/activate && uvicorn src.api.app:app --reload --port 8000
# dokumentacja: http://localhost:8000/docs


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API działa poprawnie"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    if request.asset_name.lower() != "gold":
        raise HTTPException(status_code=400, detail="Required input needs to be: 'gold'")

    input_df = get_latest_features()
    probability = model.predict_proba(input_df)[:, 1][0]
    prediction = "long" if probability >= 0.70 else "no_trade"

    return PredictResponse(
        prediction=prediction,
        probability=round(float(probability), 4),
    )

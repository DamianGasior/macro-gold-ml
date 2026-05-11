import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Gold Prediction API",
    description="API do predykcji kierunku złota za pomocą modelu LGBM",
    version="0.1.0",
)

# Ładujemy model i kolumny raz przy starcie serwera — nie przy każdym requeście
# Gdybyśmy ładowali przy każdym requeście, każde zapytanie czekałoby na odczyt z dysku
try:
    model = joblib.load("models/lgbm_classifier.pkl")
    feature_columns = joblib.load("models/feature_columns.pkl")
except FileNotFoundError:
    raise RuntimeError("Nie znaleziono plików modelu. Uruchom najpierw pipeline treningowy.")


# Pydantic — definiujemy jak ma wyglądać body requesta
# dict[str, float] = słownik gdzie klucze to nazwy features, wartości to liczby
class PredictRequest(BaseModel):
    features: dict[str, float]


# Pydantic — definiujemy jak ma wyglądać body odpowiedzi
class PredictResponse(BaseModel):
    prediction: str  # "long" lub "no_trade"
    probability: float  # pewność modelu (0.0 - 1.0)
    features_received: int  # ile features dostaliśmy (do debugowania)


# to start your local server,
#  run this in terminal : source venv/bin/activate && uvicorn src.api.app:app --reload --port 8000
"""source venv/bin/activate          → aktywuje środowisko wirtualne (venv)
&&                                → jeśli poprzednie się udało, wykonaj następne
uvicorn src.api.app:app           → uruchamia serwer, ładuje model do RAM
--reload                          → restartuje automatycznie gdy zmienisz kod
--port 8000                       → nasłuchuje na porcie 8000
Jedna uwaga — --reload powoduje że uvicorn restartuje się przy każdej zmianie pliku.
 To znaczy że joblib.load odpala się ponownie przy każdym restarcie.
   Na developmencie to normalne i wygodne. Na produkcji nie używasz --reload."""
# http://localhost:8000/docs , w ten sposob uruchamisz lokalny serwer
# co to jest pydantic ?  po co to


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API działa poprawnie"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    # Sprawdzamy czy przysłano wszystkie wymagane kolumny
    missing = [col for col in feature_columns if col not in request.features]
    if missing:
        raise HTTPException(
            status_code=400, detail=f"Brakuje {len(missing)} features: {missing[:5]}..."
        )

    # Budujemy DataFrame w dokładnie takiej kolejności kolumn jak podczas trenowania
    # Model LGBM jest wrażliwy na kolejność — musi być identyczna jak w X_train
    input_df = pd.DataFrame([request.features])[feature_columns]

    # Predykcja — predict_proba zwraca [[prob_klasa_0, prob_klasa_1]]
    # bierzemy [:, 1] czyli prawdopodobieństwo klasy 1 (long)
    probability = model.predict_proba(input_df)[:, 1][0]

    # Używamy tego samego progu co podczas trenowania (70. percentyl)
    prediction = "long" if probability >= 0.70 else "no_trade"

    return PredictResponse(
        prediction=prediction,
        probability=round(float(probability), 4),
        features_received=len(request.features),
    )

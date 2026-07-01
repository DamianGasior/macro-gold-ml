from collections import deque
from datetime import datetime, timedelta
import logging
import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.logging_config import setup_logging
from pydantic import BaseModel
from src.api_providers.common_df_merger.multiple_dataframe_transformer import Multiple_df_manager
from src.ml_work.feature_engineering.feature_engineering_regression_lgbm import (
    FeatureRegressionEngineeringLGBMR,
)
from src.pipeline.pipeline import DataPipeline
from src.pipeline.utils import SYMBOL_MAPPINGS, TWELVE_DATA, FRED
from src.llm.gold_analysis import pre_pipeline, pipeline
from src.llm.chat import Chat_history

setup_logging()
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Gold Prediction API",
    description="API do predykcji kierunku złota za pomocą modelu LGBM",
    version="0.1.0",
)

# serwuje pliki z folderu static/ pod ścieżką /static
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return FileResponse("static/index.html")


# Model i feature_columns ładowane raz przy starcie serwera
try:
    model = joblib.load("models/lgbm_classifier.pkl")
    feature_columns = joblib.load("models/feature_columns.pkl")
except FileNotFoundError:
    raise RuntimeError("Nie znaleziono plików modelu. Uruchom najpierw pipeline treningowy.")

# Below Was used in the POST endpoint, leaving it here, might be reused in the future
# together with the method @app.post("/predict", response_model=PredictResponse)

# class PredictRequest(BaseModel):
#     asset_name: str
# def predict(request: PredictRequest):


class PredictResponse(BaseModel):
    prediction: str  # "long" lub "no_trade"
    probability: float  # pewność modelu (0.0 - 1.0)


class ChatRequest(BaseModel):
    question: str
    uuid: str | None = None

    # @property
    # def id_check(self):
    #     logger.info(f"self.uuid is : {self.uuid}")
    #     logger.info(f"self.uuid is type: {type(self.uuid)}")
    #     return self.uuid


class ChatResponse(BaseModel):
    response: str
    uuid: str

    @staticmethod
    def request_chat_history(id, chat_instance):
        chat_instance = Chat_history
        chat_hist = chat_instance.return_chat_history_based_on_id(id)
        return chat_hist


# Cache w pamięci — dane rynkowe zmieniają się raz dziennie, nie ma sensu odpytywać API przy każdym requeście
_cache: dict = {"data": None, "expires_at": datetime.min}

_chat_sessions: dict = {}


def get_latest_features() -> pd.DataFrame:
    if _cache["data"] is not None and datetime.now() < _cache["expires_at"]:
        return _cache["data"]

    # Twelve Data: ceny rynkowe (ETF, surowce, krypto)
    twelve_symbols = deque(TWELVE_DATA)
    twelve_data = DataPipeline().run_requests(twelve_symbols, "twelve", SYMBOL_MAPPINGS, 200)

    # FRED: waluty, VIX, wskaźniki makro
    fred_symbols = deque(FRED)
    fred_data = DataPipeline().run_requests(fred_symbols, "fred", SYMBOL_MAPPINGS, 500)

    merged = Multiple_df_manager()
    merged.multiple_df_manager_pipeline(twelve_data)
    merged.multiple_df_manager_pipeline(fred_data)
    df_final = merged.df

    fe = FeatureRegressionEngineeringLGBMR()
    fe.feature_enginerring_pipeline(df_final)

    # Bierzemy ostatni kompletny wiersz (najnowszy dzień bez NaN)
    df_features = fe.df.dropna()
    result = df_features[feature_columns].iloc[[-1]]

    _cache["data"] = result
    _cache["expires_at"] = datetime.now() + timedelta(hours=12)
    return result


# uruchomienie lokalne:
# source venv/bin/activate && uvicorn src.api.app:app --reload --port 8000
# dokumentacja: http://localhost:8000/docs


@app.on_event("startup")
def startup_event():
    logger.info("Startup: pre-warming cache...")
    get_latest_features()
    logger.info("Startup: cache ready")


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API działa poprawnie"}


# Below is the implemention for POST, cam ne resued in the future, if required

# @app.post("/predict", response_model=PredictResponse)
# def predict(request: PredictRequest):
#     if request.asset_name.lower() != "gold":
#         raise HTTPException(status_code=400, detail="Required input needs to be: 'gold'")

#     input_df = get_latest_features()
#     probability = model.predict_proba(input_df)[:, 1][0]
#     prediction = "long" if probability >= 0.70 else "no_trade"

#     return PredictResponse(
#         prediction=prediction,
#         probability=round(float(probability), 4),
#     )


@app.get("/predict/gold", response_model=PredictResponse)
def predict():
    # if request.asset_name.lower() != "gold":
    #     raise HTTPException(status_code=400, detail="Required input needs to be: 'gold'")

    input_df = get_latest_features()
    probability = model.predict_proba(input_df)[:, 1][0]
    prediction = "long" if probability >= 0.70 else "no_trade"

    return PredictResponse(
        prediction=prediction,
        probability=round(float(probability), 4),
    )


@app.post("/post/chat")
def chat(request: ChatRequest):
    logger.debug(f"request.question is:{request.question}")
    logger.debug(f"request.uuid is:{request.uuid}")
    session_id = request.uuid
    logger.info(f"request.uuid is : {request.uuid}")
    logger.info(f"request.uuid is type: {request.uuid}")
    # for key in  _chat_sessions.keys():
    #     logger.debug(f"key iin chat session is:{key}")

    # wykorzystac _cache:
    if request.uuid is None:
        id, chat_history = pre_pipeline()
        # logger.debug(f"request.id:{id}")
        # logger.debug(f"request.id:{type(id)}")
        users_query = request.question
        request.uuid = str(id)
        # logger.debug(f"request.uuid:{request.uuid}")

        logger.debug(f"chat_history type:{type(chat_history)}")
        logger.debug(f"chat_history :{chat_history}")

        response_with_context, answer_from_model = pipeline(users_query, chat_history, id)
        logger.debug(f"answer_from_model:{answer_from_model}")
        logger.debug(f"response_with_context:{response_with_context}")
        logger.debug(f"response_with_context type:{type(response_with_context)}")

        full_chat_history = []

        full_chat_history.extend([*chat_history, *response_with_context])

        _chat_sessions[request.uuid] = full_chat_history
        logger.debug(f"full_chat_history:{full_chat_history}")
        logger.debug(f"full_chat_history type:{type(full_chat_history)}")
        # logger.debug(f"request.uuid:{request.uuid}")
        return ChatResponse(response=answer_from_model, uuid=str(request.uuid))

        # id = request.uuid
    elif _chat_sessions.get(session_id) is not None:
        logger.debug(session_id)  # bd6a0a83-6d2e-45a3-8d94-1b42c62014f5
        # if test_id in _chat_sessions:
        #     print('true_key')
        users_query = request.question
        # for key ,value in _chat_sessions.items():
        #     print (f'key_is:{key}')
        retrieved_chat = _chat_sessions[request.uuid]  #

        logger.debug(f"retrieved_chat type:{type(retrieved_chat)}")
        logger.debug(f"retrieved_chat :{retrieved_chat}")

        response_with_context, answer_from_model = pipeline(
            users_query, retrieved_chat, request.uuid
        )
        logger.debug(f"answer_from_model:{answer_from_model}")
        logger.debug(f"response_with_context:{response_with_context}")

        full_chat_history = []

        full_chat_history.extend([*retrieved_chat, *response_with_context])

        _chat_sessions[request.uuid] = full_chat_history

        return ChatResponse(response=answer_from_model, uuid=str(request.uuid))

    else:
        return "No solution yet"


# przypisz uuid4() w pre-pipeliine, niech metoda zwroci uuid4 rowniez
# dodaj cala histtorie i liste do dict ktora stworzysz  w schemacie uuid- : self._conv_in_list z chat history, wykorzystaj ten dict  # self._saved_chats = {}
# jesli odpalisz jeszcze raz zapytanie, to user id rowniez bedzie przypisany jako atrybut klasy chat Request
# jesli atrybut bedzie none / nie bedzie etgo w dict w Chat history, to strzel od poczatku pipeline, ale jesli bedzie
# to pobierz historie, wrzuc context i daj wtedy nowe pytanie do llm modelu

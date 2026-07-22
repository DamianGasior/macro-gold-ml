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
from contextlib import asynccontextmanager
from src.llm.rag.scraper import scraper_start
from src.llm.rag.indexer import index_side_chunks
import asyncio

setup_logging()
logger = logging.getLogger(__name__)


# to start locally
# source venv/bin/activate && uvicorn src.api.app:app --reload --port 8000
# docs: http://localhost:8000/docs


@asynccontextmanager
async def app_startup(app: FastAPI):
    # ==== Startup : code before yield ====
    # starts only once, when server is up
    logger.info("Startup: pre-warming cache...")
    asyncio.create_task(rag_startup())
    get_latest_features()
    logger.info("Startup: cache ready")
    app.state.rag_status = "building"
    logger.info(f"app.state.rag_status : {app.state.rag_status}")
    yield
    # ==== Shutdown : technically we are not closing the connection, will be closed with the Azure Container  ====


app = FastAPI(
    title="Gold Prediction API",
    description="API do predykcji kierunku złota za pomocą modelu LGBM",
    version="0.1.0",
    lifespan=app_startup,
)

# Serves static files (the frontend) from the folder on disk under a URL prefix.
# app.mount()  - plugs a whole URL subsection into the app
#   "/static"                                 -> URL address, e.g. my_domain.com/static/...
#   StaticFiles(directory="frontend_static")  -> folder ON DISK where the files live
#   name="static"                             -> internal label FastAPI uses to generate links
# NOTE: "/static" (URL) and "frontend_static" (folder) are two DIFFERENT things.
app.mount("/static", StaticFiles(directory="frontend_static"), name="static")


@app.get("/")
def root():
    """Serve the frontend homepage.

    When a user hits the root URL "/", this endpoint returns index.html directly,
    so they don't have to type /static/index.html manually - the server does it for them.
    """
    return FileResponse("frontend_static/index.html")


# Model i feature_columns are loaded during server start process
try:
    model = joblib.load("models/lgbm_classifier.pkl")
    feature_columns = joblib.load("models/feature_columns.pkl")
except FileNotFoundError:
    raise RuntimeError("There are no model files. Start first the training plan.")

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


# Cache in memory - market data are chaning once a day, there is no sense to request api multiple times a day
_cache: dict = {"data": None, "expires_at": datetime.min}

_chat_sessions: dict = {}


def get_latest_features() -> pd.DataFrame:
    if _cache["data"] is not None and datetime.now() < _cache["expires_at"]:
        return _cache["data"]

    # Twelve Data: market data (ETF, comm, crypto)
    twelve_symbols = deque(TWELVE_DATA)
    twelve_data = DataPipeline().run_requests(twelve_symbols, "twelve", SYMBOL_MAPPINGS, 200)

    # FRED: ccy, VIX, macro datat
    fred_symbols = deque(FRED)
    fred_data = DataPipeline().run_requests(fred_symbols, "fred", SYMBOL_MAPPINGS, 500)

    merged = Multiple_df_manager()
    merged.multiple_df_manager_pipeline(twelve_data)
    merged.multiple_df_manager_pipeline(fred_data)
    df_final = merged.df

    fe = FeatureRegressionEngineeringLGBMR()
    fe.feature_enginerring_pipeline(df_final)

    # we take the last row with data ( the latest without NaN)
    df_features = fe.df.dropna()
    result = df_features[feature_columns].iloc[[-1]]

    _cache["data"] = result
    _cache["expires_at"] = datetime.now() + timedelta(hours=12)
    return result


async def rag_startup():
    try:
        await asyncio.to_thread(rag_pipeline)
        app.state.rag_status = "completed"
        logger.info(f"app.state.rag_status: {app.state.rag_status}")

    except Exception as e:
        app.state.rag_status = "failed"
        logger.info(f"app.state.rag_status: {app.state.rag_status}")
        logger.warning(f"RAG process failed with error : {e}")


def rag_pipeline():
    chunks = scraper_start()
    index_side_chunks(chunks)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API works correctly"}


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

        # logger.debug(f"chat_history type:{type(chat_history)}")
        logger.debug(f"chat_history :{chat_history}")

        response_with_context, answer_from_model = pipeline(users_query, chat_history, id)
        logger.debug(f"answer_from_model:{answer_from_model}")
        logger.debug(f"response_with_context:{response_with_context}")
        logger.debug(f"response_with_context type:{type(response_with_context)}")
        if app.state.rag_status != "completed":
            answer_from_model += "\n Note: analytical articles are not available right now — this answer is based on market data only."
            logger.debug(f"RAG process  status:{app.state.rag_status}")

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

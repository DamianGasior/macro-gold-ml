from collections import deque
import joblib
from openai import OpenAI
from dotenv import load_dotenv
import logging
from src.api_providers.common_df_merger.multiple_dataframe_transformer import Multiple_df_manager
from src.ml_work.feature_engineering.feature_engineering_regression_lgbm import (
    FeatureRegressionEngineeringLGBMR,
)
from src.pipeline.pipeline import DataPipeline
from src.llm.chat import Chat_history
from src.llm.rag.retriever import search, format_context
from datetime import datetime
from zoneinfo import ZoneInfo
from src.pipeline.utils import SYMBOL_MAPPINGS, TWELVE_DATA, FRED
import uuid

logger = logging.getLogger(__name__)

# OPENAI SDK has it own logs, on DEBUG level, those you need to hide separetely, hence config below :
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


load_dotenv()
client = OpenAI()

model = joblib.load("models/lgbm_classifier.pkl")
feature_columns = joblib.load("models/feature_columns.pkl")


USER_CONTEXT = {
    "role": "system",
    "content": """You are a gold market analyst with a medium and long-term perspective.
You interpret technical and macroeconomic data for XAU/USD (spot gold).

Rules:
- Base your analysis solely on the provided data
- Look for analogies in gold market history
- Instead of hallucinating say: 'insufficient data to assess'
- Answer in English, concisely — maximum 4 sentences""",
}


def fetch_latest_features():
    twelve_symbols = deque(TWELVE_DATA)
    twelve_data = DataPipeline().run_requests(twelve_symbols, "twelve", SYMBOL_MAPPINGS, 200)

    fred_symbols = deque(FRED)
    fred_data = DataPipeline().run_requests(fred_symbols, "fred", SYMBOL_MAPPINGS, 500)

    merged = Multiple_df_manager()
    merged.multiple_df_manager_pipeline(twelve_data)
    merged.multiple_df_manager_pipeline(fred_data)

    fe = FeatureRegressionEngineeringLGBMR()
    fe.feature_enginerring_pipeline(merged.df)
    return fe.df.dropna()


def get_lgbm_signal(df) -> dict:
    input_df = df[feature_columns].iloc[[-1]]
    probability = model.predict_proba(input_df)[:, 1][0]
    prediction = "LONG" if probability >= 0.70 else "NO TRADE"
    return {"prediction": prediction, "probability": round(float(probability), 4)}


def build_market_context(df, lgbm_signal: dict) -> str:
    logger.debug(f"Received data is :{df}")
    columns = list(SYMBOL_MAPPINGS.values())
    logger.debug(f"Latest columns are :{columns}")

    df_with_data = df.copy()
    df_with_data_ = df_with_data[columns]
    df_with_data_filtered = df_with_data_
    logger.debug(f"df_with_data_filtered :{df_with_data_filtered.tail(15)}")

    latest = df.iloc[-1]
    date = df.index[-1]
    logger.info(f"Latest data are available for date :{date}")
    logger.debug(f"Latest data is :{latest}")
    return f"""


Date: {date.strftime('%Y-%m-%d')}

LGBM model signal:
- Recommendation: {lgbm_signal['prediction']}
- Probability (long): {lgbm_signal['probability']:.1%}

XAU/USD (spot gold):
- Daily return: {latest['GOLD_return']:.4%}
- 5-day return: {latest['GOLD_return_5']:.4%}
- 20-day return: {latest['GOLD_return_20']:.4%}
- Trend regime: >0 = price above moving average = uptrend; <0 = price below moving average = downtrend
- 10-day trend: {latest['GOLD_trend_regime_10']:.0f} (1=above MA, -1=below MA)
- 20-day trend: {latest['GOLD_trend_regime_20']:.0f}
- 30-day trend: {latest['GOLD_trend_regime_30']:.0f}
- 20-day volatility: {latest['GOLD_vol_20']:.4%}

Market context:
- VIX daily return: {latest['CBOE_VIX_return']:.4%}
- SPY 5-day return: {latest['SPY_return_5']:.4%}
- WTI Oil return: {latest['WTI_return']:.4%}
- DXY (dollar) return: {latest['DXY_return']:.4%}
- Gold and main indices price table, last 15 days: {df_with_data_filtered.tail(15)}
"""


# def ask_llm(context: str, question: str) -> str:
def ask_llm(*args) -> str:
    messages_updated = []
    for arg in args:  # this loop was for debugginh purpose
        logger.debug(f"messages_updated:{messages_updated}")
        logger.debug(f"type messages_updated:{type(messages_updated)}")
        # for i in messages_updated:
        #     logger.debug(i)

        logger.debug(arg)
        logger.debug(type(arg))
        if isinstance(arg, list):
            if len(messages_updated) == 0:
                messages_updated = list(arg)
            else:
                messages_updated.extend(arg)
        else:
            messages_updated.append(arg)

    logger.debug(messages_updated)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        max_tokens=300,
        messages=messages_updated,
    )

    logger.debug(f"response dir {dir(response)}")
    logger.debug(f"response_choices dir {dir(response.choices[0])}")

    return response.choices[0].message.content


def get_news_context(question: str, n_results: int = 5) -> str:
    """Queries ChromaDB and returns a formatted text block from articles matching the question."""
    try:
        chunks = search(question, n_results=n_results)
        return format_context(chunks)
    except Exception as e:
        logger.warning(f"RAG unavailable: {e}")
        return ""


def define_users_input(**kwargs):
    my_dict = {}
    my_dict.update(kwargs)
    logger.debug(my_dict)
    return my_dict


def define_time():
    now_cet = datetime.now(ZoneInfo("Europe/Warsaw"))
    timestamp = now_cet.strftime("%Y-%m-%d_%HH-%MM-%SS")
    return timestamp


def users_input_text():
    text = input("Write  your questions or comment. If you want to end the chat wirte 'close' : ")
    return text


def pipeline(qeury_from_users, rec_chat_history, id):

    updated_chat_history = Chat_history()

    # while True:
    users_qq = qeury_from_users
    # if users_qq == "close":
    #     logger.debug("Closing this chat.")
    #     break

    news_context = get_news_context(users_qq)
    if news_context:
        content = f"{users_qq}\n\nRelated analytical articles:\n{news_context}"
        logger.debug(
            f"Related analytical articles: {news_context}\n in response to user question: {users_qq}"
        )

    else:
        content = users_qq

    users_qq_attached = define_users_input(role="user", content=content)
    logger.debug(f"rec_chat_history:{rec_chat_history}")
    logger.debug(f"rec_chat_history type:{type(rec_chat_history)}")
    response = ask_llm(rec_chat_history, users_qq_attached)
    logger.debug(f"Users question was : {users_qq}")
    logger.debug(f"Response from the LLM model is : {response}")
    # print(f"Response from the LLM model is : {response}")
    updated_chat_history.list_expansion(users_qq_attached)
    updated_chat_history.list_expansion(define_users_input(role="assistant", content=response))

    updated_chat_history.expand_chat_with_id(id)
    # whole_context=updated_chat_history.return_chat_history_based_on_id(id)
    whole_context = updated_chat_history.return_list_chat()

    logger.debug(f"chat_history:{whole_context}")
    logger.debug(f"chat_history type:{type(whole_context)}")

    # whole_context=chat_history.return_chat_history_based_on_id(id)
    return whole_context, f"Response from the LLM model is : {response}"


def pre_pipeline():
    id_assigned = uuid.uuid4()
    logger.debug(f"id_assigned :{id_assigned}")
    logger.debug(f"id_assigned type :{type(id_assigned)}")

    draft_chat_history = Chat_history()

    logger.info("Fetching market data...")
    df = fetch_latest_features()
    logger.debug(f"columns of the df used are : {df.columns}")
    logger.debug(f"tail of the df is :{df.tail(20)}")

    lgbm_signal = get_lgbm_signal(df)
    context = build_market_context(df, lgbm_signal)
    draft_chat_history.list_expansion(USER_CONTEXT)

    logger.info("\n--- Context sent to LLM ---")
    logger.info(context)
    question = "The LGBM model issued a recommendation. Do the technical and macro data confirm or contradict it? Justify."

    logger.info("Fetching article context (RAG)...")
    news_context = get_news_context("gold price outlook macro factors dollar inflation")
    logger.info(
        f"RAG returned context:\n{news_context[:300]}..."
        if news_context
        else "RAG: no articles in database"
    )

    users_input = define_users_input(
        role="user",
        content=f"Here is the current market data:\n{context}\n\nContext from analytical articles:\n{news_context}\n\nQuestion: {question}",
    )
    draft_chat_history.list_expansion(users_input)

    logger.info("\n--- LLM analysis ---")
    response_from_llm = ask_llm(USER_CONTEXT, users_input)
    logger.info(response_from_llm)
    converted_resposne = define_users_input(role="assistant", content=response_from_llm)
    draft_chat_history.list_expansion(converted_resposne)

    logger.info("\n--- summary of conversation in  LLM ---")
    draft_chat_history.expand_chat_with_id(id_assigned)
    list_of_chat_histry = draft_chat_history.return_list_chat_history()
    return id_assigned, list_of_chat_histry


if __name__ == "__main__":
    from src.logging_config import setup_logging

    setup_logging(level=logging.DEBUG)
    id_received, draft_chat_history = pre_pipeline()
    users_query = users_input_text()
    pipeline(users_query, draft_chat_history, id_received)

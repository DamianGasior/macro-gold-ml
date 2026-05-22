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
from datetime import datetime
from zoneinfo import ZoneInfo
from src.pipeline.utils import SYMBOL_MAPPINGS

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
    "content": """Jesteś analitykiem rynku złota z perspektywą średnio i długoterminową.
Interpretujesz dane techniczne i makroekonomiczne dotyczące ETF na złoto (GLD).

Zasady:
- Opieraj się wyłącznie na dostarczonych danych
- Szukaj analogii w historii rynków złota
- Zamiast halucynować powiedz: 'brak danych do oceny'
- Odpowiadaj po polsku, zwięźle — maksymalnie 4 zdania""",
}


def fetch_latest_features():
    twelve_symbols = deque(["GLD", "SPY", "USO", "BNO", "BTC/USD"])
    twelve_data = DataPipeline().run_requests(twelve_symbols, "twelve", SYMBOL_MAPPINGS, 200)

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

    fe = FeatureRegressionEngineeringLGBMR()
    fe.feature_enginerring_pipeline(merged.return_df)
    return fe.return_dataframe.dropna()


def get_lgbm_signal(df) -> dict:
    input_df = df[feature_columns].iloc[[-1]]
    probability = model.predict_proba(input_df)[:, 1][0]
    prediction = "LONG" if probability >= 0.70 else "NO TRADE"
    return {"prediction": prediction, "probability": round(float(probability), 4)}


def build_market_context(df, lgbm_signal: dict) -> str:
    latest = df.iloc[-1]
    date = df.index[-1]
    logger.info(f"Latest data are available for date :{date}")
    logger.debug(f"Latest data is :{latest}")
    return f"""


Data: {date.strftime('%Y-%m-%d')}

Sygnał modelu LGBM:
- Rekomendacja: {lgbm_signal['prediction']}
- Prawdopodobieństwo (long): {lgbm_signal['probability']:.1%}

Złoto (GLD):
- Dzienny zwrot: {latest['GOLD_return']:.4%}
- Zwrot 5-dniowy: {latest['GOLD_return_5']:.4%}
- Zwrot 20-dniowy: {latest['GOLD_return_20']:.4%}
- Gold trend regime below , interpetation : if >0 , price is above average = uptrend ; if <0 , price is below average = downtrend
- Trend 10-dniowy: {latest['GOLD_trend_regime_10']:.0f} (1=powyżej MA, -1=poniżej)
- Trend 20-dniowy: {latest['GOLD_trend_regime_20']:.0f}
- Trend 30-dniowy: {latest['GOLD_trend_regime_30']:.0f}
- Zmiennosc 20-dniowa: {latest['GOLD_vol_20']:.4%}

Rynek (kontekst):
- VIX dzienny zwrot: {latest['CBOE_VIX_return']:.4%}
- SPY zwrot 5-dniowy: {latest['SPY_return_5']:.4%}
- Ropa WTI zwrot: {latest['WTI_return']:.4%}
- DXY (dolar) zwrot: {latest['DXY_return']:.4%}
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

    return response.choices[0].message.content


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


def pipeline(chat_history: Chat_history):
    while True:
        users_qq = users_input_text()
        if users_qq == "close":
            logger.debug("Closing this chat.")
            break
        users_qq_attached = define_users_input(role="user", content=users_qq)
        # logger.debug(users_qq_attached)
        resposne = ask_llm(chat_history.return_list_chat_history, users_qq_attached)
        # logger.debug(resposne)
        chat_history.list_expansion(users_qq_attached)
        # chat_history.return_list_chat_history
        chat_history.list_expansion(define_users_input(role="assistant", content=resposne))


if __name__ == "__main__":
    from src.logging_config import setup_logging

    setup_logging(level=logging.INFO)

    draft_chat_history = Chat_history()

    logger.info("Pobieranie danych rynkowych...")
    df = fetch_latest_features()
    logger.debug(f"columns of the df used are : {df.columns}")
    logger.debug(f"head of the df is :{df.head(20)}")

    lgbm_signal = get_lgbm_signal(df)
    context = build_market_context(df, lgbm_signal)
    draft_chat_history.list_expansion(USER_CONTEXT)

    logger.info("\n--- Kontekst wysłany do LLM ---")
    logger.info(context)
    question = "Model LGBM wydał rekomendację. Czy dane techniczne i makro ją potwierdzają czy przeczą? Uzasadnij."
    users_input = define_users_input(
        role="user", content=f"Oto aktualne dane rynkowe:\n{context}\n\nPytanie: {question}"
    )
    draft_chat_history.list_expansion(users_input)

    logger.info("\n--- Analiza LLM ---")
    reponse_from_llm = ask_llm(USER_CONTEXT, users_input)
    logger.info(reponse_from_llm)
    converted_resposne = define_users_input(role="assistant", content=reponse_from_llm)
    draft_chat_history.list_expansion(converted_resposne)

    logger.info("\n--- summary of conversation in  LLM ---")
    draft_chat_history.return_list_chat_history

    pipeline(draft_chat_history)

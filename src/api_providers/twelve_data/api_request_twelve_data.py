import requests
from requests_cache import CachedSession
import logging
from .single_tranformation import Data_transformation
from ...pipeline.base_api_request import BaseAPIProvider
import os
from dotenv import load_dotenv

# Global HTTP client with persistent caching (SQLite backend).
# Caches responses for identical requests (same URL + params) for 2 hours
session = CachedSession("demo_cache", backend="sqlite", expire_after=7200)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv()  # its loading all variables from .env into os.environ
API_KEY = os.getenv(
    "TWELVE_DATA_API_KEY"
)  # picking up the right variable and taking the correct key


def api_request_cached(parameters):
    url = "https://api.twelvedata.com/time_series"
    resp = session.get(url, params=parameters)
    resp.raise_for_status()  # its a ready method from 'requests' module, where following htpp responses 400 <= resp.status_code < 600 are checked
    return {
        "from_cache": getattr(resp, "from_cache", False),
        "data": resp.json(),
        "status_code": resp.status_code,
    }


class Underlying_twelve_data_reuquest(BaseAPIProvider):

    def __init__(
        self,
        symbol,
        adjust="adjusted",  # "non-adjusted"],  # this is driven already by the users input
        interval="1day",  # Supported intervals: 1min, 5min, 15min, 30min, 45min, 1h, 2h, 4h, 8h, 1day, 1week, 1month'
        outputsize=5000,
        dp=4,
        previous_close=True,
        apikey=API_KEY,
    ):
        super().__init__(symbol)  # executing the constructor of base class
        self.apikey = apikey
        self.interval = interval
        self.outputsize = outputsize  # max is 5000
        self.dp = dp
        self.previous_close = previous_close
        self.adjust = adjust

    def to_dict_params(self):
        params = {
            "symbol": self.symbol,
            "interval": self.interval,
            "outputsize": self.outputsize,
            "dp": self.dp,
            "previous_close": self.previous_close,
            "adjust": self.adjust,
            "apikey": self.apikey,
        }
        return params

    def api_request(self):
        parameters = self.to_dict_params()
        # url = "https://api.twelvedata.com/time_series?"
        try:
            # resp = requests.get(url, params=parameters)
            response = api_request_cached(
                parameters
            )  # object Resposne in the library requests have an featrure called .status_code, which may return :  200, 404, 500
            # print(type(resp))  # <class 'requests.models.Response'>
            log_info = response.get("from_cache")
            resp = response.get("data")
            if resp is None:
                raise Exception("Missing key 'data' in the api resposne from twelve data")
            logger.info(f"API response is recevied based on caches: {log_info}")
            # print(type(response))  # <class 'dict'>
            # if resp.status_code == 200
            code = resp.get("code")
            message = resp.get("message")
            resp_status_code = response.get("status_code")
            logger.info(f"Response type is : {resp_status_code}")
            logger.debug(f"Response is : {resp}")

            if resp_status_code == 200:
                # for success scenario
                if "meta" in resp:
                    logger.info(f"Request was executed succefully for symbol: {self.symbol}")
                    symbol_received = resp["meta"]["symbol"]
                    # st.session_state.success_symbols
                    if symbol_received:
                        logger.info(f"""Data received for  symbol: {symbol_received}""")
                    return resp

                # in case API will come back with an error
                elif "code" in resp.keys():
                    logger.info(f"Response type is : {code}. Response is {message}")
                    raise Exception(f'Broker error  {resp.get("code")} : {resp.get("message")}')
                else:
                    raise Exception(f"Unexpected response {resp}")
            else:
                raise ConnectionError(f"Unexpected HTTP status {resp_status_code} from twelve_data")

        except requests.RequestException as e:
            raise Exception(f"Transport erorr{e}")  # thanks to that we will get one f-string , ane
            # will be not getting this error :
            # TypeError: AlertMixin.error() takes 2 positional arguments but 3 were given
            # when it would implemented like this : st.error("Error occured", e)

    def execute_full_request(self):
        logger.info("request_executed_to_twelve_data")
        response = self.api_request()  # blocking it to check the st.cache_Data
        # print(response)
        return response

    def response_from_api(self, api_reponse):
        logger.info(f"api resposne type is : {type(api_reponse)}")
        logger.info(f"Resposne from api is :{api_reponse}")
        symbol = self.symbol
        api_reponse = self.to_dict()
        api_reponse = api_reponse["quotes"]

        return Data_transformation(api_reponse, symbol)

    def to_dict(self):
        response = self.api_request()
        data = response["values"]
        return {"symbol": self.symbol, "quotes": data}

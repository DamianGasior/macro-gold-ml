import requests
import logging
from requests_cache import CachedSession
from .single_transformation_fred import Data_fred_transformation
from ...pipeline.base_api_request import BaseAPIProvider
import os
from dotenv import load_dotenv

session = CachedSession("demo_cache", backend="sqlite", expire_after=7200)

logger = logging.getLogger(__name__)


load_dotenv()
API_KEY = os.getenv("FRED_API_KEY")

# dodac observation start i end date


def api_request_cached(parameters):
    url = "https://api.stlouisfed.org/fred/series/observations?"
    resp = session.get(url, params=parameters)
    resp.raise_for_status()  # its a ready method from 'requests' module, where following htpp responses 400 <= resp.status_code < 600 are checked
    logger.debug(resp)
    return {
        "from_cache": getattr(resp, "from_cache", False),
        "data": resp.json(),
        "status_code": resp.status_code,
    }


class Fred_request_api(BaseAPIProvider):
    def __init__(
        self,
        symbol,
        api_key=API_KEY,
        file_type="json",
        observation_start="1999-05-25",
        observation_end="9999-12-31",
    ):
        super().__init__(symbol)
        self.api_key = api_key
        self.file_type = file_type
        self.observation_start = observation_start
        self.observation_end = observation_end

    def to_dict_params(self):
        return {
            "series_id": self.symbol,
            "api_key": self.api_key,
            "file_type": self.file_type,
            "observation_start": self.observation_start,
            "observation_end": self.observation_end,
        }

    def api_request(self):
        parameters = self.to_dict_params()

        try:
            resp = api_request_cached(parameters)
            # print(resp)
            # print(type(resp))  # <class 'requests.models.Response'>
            # print(resp.get("data"))
            # print(type(response))
            logger.info(f"Response type is : {resp.get("status_code")}")
            logger.info(f"Response type is from cache: {resp.get("from_cache")}")
            logger.info(f"Response is : {resp.get("data")}")
            response = resp.get("data")
            return response

        except requests.RequestException as e:
            raise Exception(f"Transport erorr{e}")  # thanks to that we will get one f-string , ane
            # will be not getting this error :
            # TypeError: AlertMixin.error() takes 2 positional arguments but 3 were given
            # when it would implemented like this : st.error("Error occured", e)

    def execute_full_request(self):
        logger.info("request_executed_to_fred")
        response = self.api_request()
        return response

    def response_from_api(self, api_reponse):
        series_id = self.symbol
        api_reponse = self.to_dict()
        api_reponse = api_reponse["quotes"]
        return Data_fred_transformation(api_reponse, series_id)

    def to_dict(self):
        # print('druk metody to_dict')
        response = self.api_request()
        data = response["observations"]
        return {"symbol": self.symbol, "quotes": data}

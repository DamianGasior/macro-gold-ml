import requests
import logging
from flask import Flask
from flask_caching import Cache
import time

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


API_KEY = "fbdae593317d45162a3c4a3ebc6a74ec"

# dodac observation start i end date


def api_request_cached(parameters):
    url = "https://api.stlouisfed.org/fred/series/observations?"
    resp = requests.get(url, params=parameters)
    resp.raise_for_status()  # its a ready method from 'requests' module, where following htpp responses 400 <= resp.status_code < 600 are checked
    return resp


class Fred_request_api:
    def __init__(
        self,
        series_id,
        api_key=API_KEY,
        file_type="json",
        observation_start="2026-01-01",
        observation_end="9999-12-31",
    ):
        self.series_id = (series_id,)
        self.api_key = (api_key,)
        self.file_type = file_type
        self.observation_start = observation_start
        self.observation_end = observation_end

    def to_dict_params(self):
        return {
            "series_id": self.series_id,
            "api_key": self.api_key,
            "file_type": self.file_type,
            "observation_start": self.observation_start,
            "observation_end": self.observation_end,
        }

    def api_request(self):
        parameters = self.to_dict_params()

        try:
            resp = api_request_cached(parameters)
            print(resp)
            # print(type(resp))  # <class 'requests.models.Response'>
            response = resp.json()
            # print(response)
            # print(type(response))
            logging.info(f"Response type is : {resp.status_code}")
            logging.info(f"Response is : {response}")
            return response

        except requests.RequestException as e:
            raise Exception(
                f"Transport erorr{e}"
            )  # thanks to that we will get one f-string , ane
            # will be not getting this error :
            # TypeError: AlertMixin.error() takes 2 positional arguments but 3 were given
            # when it would implemented like this : st.error("Error occured", e)

    def execute_full_request(self):
        logging.info("request_executed_to_fred")
        response = self.api_request()  # blocking it to check the st.cache_Data
        # print(response)
        return response

    def response_from_api(self, api_reponse):
        print(type(api_reponse))
        print(api_reponse)
        symbol = self.symbol
        api_reponse = self.to_dict()
        api_reponse = api_reponse["observations"]

        # return Data_transformation(api_reponse, symbol)

    def to_dict(self):
        # print('druk metody to_dict')
        response = self.api_request()
        data = response["values"]
        return {"symbol": self.symbol, "observations": data}


test_request = Fred_request_api("DGS10")
test_request.api_request()

# https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key=fbdae593317d45162a3c4a3ebc6a74ec&file_type=json

# /home/damian/projekty/Python/macro-fx-ml/src/api_providers/fred/api_request_fred.py

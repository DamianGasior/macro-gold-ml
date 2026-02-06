import requests
import logging
from flask import Flask
from flask_caching import Cache
import time
from .single_tranformation import Data_transformation


API_KEY = "cd8a73e98be740cca47f97db19df0301"


def api_request_cached(parameters):
    url = "https://api.twelvedata.com/time_series?"
    resp = requests.get(url, params=parameters)
    resp.raise_for_status()  # its a ready method from 'requests' module, where following htpp responses 400 <= resp.status_code < 600 are checked
    return resp


class Underlying_twelve_data_reuquest:

    def __init__(
        self,
        symbol,
        adjust="adjusted",  #  "non-adjusted"],  # this is driven already by the users input
        interval="1day",  #   Supported intervals: 1min, 5min, 15min, 30min, 45min, 1h, 2h, 4h, 8h, 1day, 1week, 1month'
        outputsize=10,
        dp=4,
        previous_close=True,
        apikey=API_KEY,
    ):
        self.apikey = apikey
        self.symbol = symbol
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
            "apikey": API_KEY,
        }
        return params

    def api_request(self):
        parameters = self.to_dict_params()
        # url = "https://api.twelvedata.com/time_series?"
        try:
            # resp = requests.get(url, params=parameters)
            resp = api_request_cached(
                parameters
            )  # object Resposne in the library requests have an featrure called .status_code, which may return :  200, 404, 500
            print(type(resp))  # <class 'requests.models.Response'>
            response = resp.json()
            print(response)
            print(type(response))  # <class 'dict'>
            # if resp.status_code == 200
            code = response.get("code")
            message = response.get("message")

            logging.info(f"Response type is : {resp.status_code}")

            if resp.status_code == 200:
                # for success scenario
                if "meta" in resp.json():
                    logging.info(
                        f"Request was executed succefully for symbol: {self.symbol}"
                    )
                    symbol_received = response["meta"]["symbol"]
                    # st.session_state.success_symbols
                    if symbol_received:
                        logging.info(
                            f"""Data received for  symbol: {symbol_received}"""
                        )
                    return response

                # in case API will come back with an error
                elif "code" in response.keys():
                    logging.info(f"Response type is : {code}. Response is {message}")
                    raise Exception(
                        f'Broker error  {response.get("code")} : {response.get("message")}'
                    )
                else:
                    raise Exception(f"Unexpected response {response}")

        except requests.RequestException as e:
            raise Exception(
                f"Transport erorr{e}"
            )  # thanks to that we will get one f-string , ane
            # will be not getting this error :
            # TypeError: AlertMixin.error() takes 2 positional arguments but 3 were given
            # when it would implemented like this : st.error("Error occured", e)

    def execute_full_request(self):
        print("request_executed_by_twelve_data")
        response = self.api_request()  # blocking it to check the st.cache_Data
        # parameters_for_req = self.to_dict_params()
        # response = api_request(parameters_for_req)

        print(response)
        return response

    def response_from_api(self, api_reponse):
        print(type(api_reponse))
        print(api_reponse)
        symbol = self.symbol
        api_reponse = self.to_dict()
        api_reponse = api_reponse["quotes"]

        return Data_transformation(api_reponse, symbol)

    def to_dict(self):
        # print('druk metody to_dict')
        response = self.api_request()
        data = response["values"]
        return {"symbol": self.symbol, "quotes": data}

    # def return_symbol(self,api_reponse):
    #     symbol=api_reponse["meta"]["symbol"]
    #     return symbol


# USD_PLN = Underlying_twelve_data_reuquest("USD/PLN")

# USD_PLN.execute_full_request()

import pandas as pd
import requests
import logging
from .single_transformation_stooq import Data_stooq_transformation
from ...pipeline.base_api_request import BaseAPIProvider
from io import StringIO

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)



# this is not an  official api from stooq, we are just calling here a specific endpoint which provides us with a csv file in a response.

# the first date for which data are provided by stooq.pl for this ticker "DGS10" is 25th May 1999


def api_request_cached(symbol, interval):
    session = requests.Session()

    url = f"https://stooq.pl/q/d/l/?s={symbol}&i={interval}"
    print(url)
    headers =  {  "User-Agent": "Mozilla/5.0",
    "Accept": "text/csv,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"}
    
    response = session.get(url, headers=headers)
    print(response.status_code)
    print(response.text[:200]) 

    if not response.text.strip():
        raise ValueError(f"Empty response from Stooq for symbol: {symbol}")

    dataframe = pd.read_csv(StringIO(response.text)).set_index("Data") # set already the 'Data' column as index, so that the 0,1,2 will be avoided.
    # print(dataframe)

 # DEBUG
  
    if dataframe.empty:
        raise ValueError(f"Empty dataframe for symbol: {symbol}")

    return dataframe


class Stooq_request_api(BaseAPIProvider):
    def __init__(self, symbol):
        super().__init__(symbol)
        self.i = "d"

    # below method will be not used in this  class, we are requesting here for a csv file, its not an get api request
    def to_dict_params(self):
        pass

    def api_request(self):

        try:
            resp = api_request_cached(self.symbol, self.i)
            print(type(resp))
            return resp
        except Exception as e:
            raise Exception(f"Data error {e}")

    def execute_full_request(self):
        logging.info("request_executed_to_stooq")
        response = self.api_request()  # blocking it to check the st.cache_Data
        print(type(response))
        return response

    def response_from_api(self, api_reponse):
        print(type(api_reponse))
        # print(api_reponse)
        symbol = self.symbol
        # api_reponse = self.to_dict()
        # api_reponse = api_reponse["quotes"]
        return Data_stooq_transformation(api_reponse, symbol)

    def to_dict(self):
        pass

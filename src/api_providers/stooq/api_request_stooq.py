import pandas as pd
import logging
from .single_transformation_stooq import Data_stooq_transformation


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# this is not an  official api from stooq, we are just calling here a specific endpoint which provides us with a csv file in a response. 


def api_request_cached(symbol,interval):
    url = f"https://stooq.pl/q/d/l/?s={symbol}&i={interval}"
    print(url)
    # url = f"https://stooq.pl/q/d/l/?{parameters}"
    # https://stooq.pl/q/d/l/?s=10yply.b&i=d

    dataframe = pd.read_csv(url).set_index('Data') # set already the 'Data' column as index, so that the 0,1,2 will be avoided.
    print(dataframe)
    return dataframe


class Stooq_request_api:
    def __init__(self, symbol):
        self.symbol = symbol
        self.i = 'd'
        

    def to_dict_params(self):
      pass
        

    def api_request(self):
              
        try:
            resp = api_request_cached(self.symbol,self.i)
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
        print(api_reponse)
        symbol = self.symbol
        # api_reponse = self.to_dict()
        # api_reponse = api_reponse["quotes"]
        return Data_stooq_transformation(api_reponse, symbol)
    

    def to_dict(self):
       pass




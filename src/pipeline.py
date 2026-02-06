from collections import deque

from src.api_providers.twelve_data.api_request_twelve_data import (
    Underlying_twelve_data_reuquest,
)
from src.api_providers.twelve_data.single_tranformation import Data_transformation


symbol_deque = deque(["USD/PLN", "EUR/USD"])

while len(symbol_deque) > 0:

    symbol = symbol_deque.popleft()

    USD_PLN = Underlying_twelve_data_reuquest(symbol)

    USD_PLN.execute_full_request()
    # symbol_USD_PLN=USD_PLN.execute_full_request()

    USD_PLN_transf = USD_PLN.response_from_api(USD_PLN)
    USD_PLN_transf.to_dataframe()
    print(type(USD_PLN_transf))

# dodac nowa metoda i nowy plyk, gdzie bede robil merge danych, np, USD, EUR
# dane musza tam byc normalizowane ( jakie to pojecie ?) do jedn jdaty

# combined_fx_dataframe

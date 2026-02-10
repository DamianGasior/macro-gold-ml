from collections import deque
from src.api_providers.common_df_merger.multiple_dataframe_transformer import (
    Multiple_df_manager,
)
from src.api_providers.twelve_data.api_request_twelve_data import Underlying_twelve_data_reuquest
from src.api_providers.fred.api_request_fred import Fred_request_api
from src.api_providers.stooq.api_request_stooq import Stooq_request_api



def main():
    
    
    symbol_fx_deque = deque(["USD/PLN", "EUR/USD"])
    if len(symbol_fx_deque) > 0:
        symbol_fx=symbol_fx_deque.popleft()
        provider=Underlying_twelve_data_reuquest(symbol_fx)

        pass

    elif broker=='Fred':
        pass

    elif borker =='Stooq':
        pass


if __name__ == '__main__':
    main()




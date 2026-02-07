from collections import deque
from src.api_providers.common_df_merger.multiple_dataframe_transformer import (
    Multiple_df_manager,
)
from src.api_providers.twelve_data.api_request_twelve_data import (
    Underlying_twelve_data_reuquest,
)
from src.api_providers.twelve_data.single_tranformation import Data_transformation
from src.api_providers.common_df_merger.multiple_dataframe_transformer import Multiple_df_manager

fx_list = Multiple_df_manager()
fx_combined_df= Multiple_df_manager()



symbol_deque = deque(["USD/PLN", "EUR/USD"])

while len(symbol_deque) > 0:

    symbol = symbol_deque.popleft()

    fx_pair = Underlying_twelve_data_reuquest(symbol)

    fx_pair.execute_full_request()
    # symbol_USD_PLN=USD_PLN.execute_full_request()

    fx_pair_transf = fx_pair.response_from_api(
        fx_pair
    )  # using a method from Underlying_twelve_data_reuquest class,
    # api where the response is passed to Data_transformation class


    fx_list.add_to_fx_list(fx_pair_transf.to_dataframe())
    fx_list.len_of_lists()


    print(type(fx_list))



fx_list.list_concacenate('fx')



print(fx_list.return_df())

# df_merged_fx=Multiple_df_manager.list_concacenate(fx_list)


# dodac nowa metoda i nowy plyk, gdzie bede robil merge danych, np, USD, EUR
# dane musza tam byc normalizowane ( jakie to pojecie ?) do jedn jdaty

# combined_fx_dataframe

from collections import deque
from src.api_providers.common_df_merger.multiple_dataframe_transformer import (
    Multiple_df_manager,
)
from src.api_providers.twelve_data.api_request_twelve_data import (
    Underlying_twelve_data_reuquest,
)
from src.api_providers.fred.api_request_fred import Fred_request_api
from src.api_providers.stooq.api_request_stooq import Stooq_request_api

# from src.api_providers.twelve_data.single_tranformation import Data_transformation
# from src.api_providers.fred.single_transformation_fred import Data_fred_transformation


fx_list = Multiple_df_manager()
fx_combined_df= Multiple_df_manager()

bond_yield_list=Multiple_df_manager()
bond_yield_combined=Multiple_df_manager()

pl_bond_yield_list=Multiple_df_manager()
pl_bond_yield_combined=Multiple_df_manager()

merged_asset_class_df=Multiple_df_manager()


symbol_fx_deque = deque(["USD/PLN", "EUR/USD"])
# symbol_fx_deque = deque([])

while len(symbol_fx_deque) > 0:
    symbol_fx = symbol_fx_deque.popleft()
    fx_pair = Underlying_twelve_data_reuquest(symbol_fx)
    fx_pair.execute_full_request()    # symbol_USD_PLN=USD_PLN.execute_full_request()
    fx_pair_transf = fx_pair.response_from_api(fx_pair)  # using a method from Underlying_twelve_data_reuquest class,
    # api where the response is passed to Data_transformation class
    fx_list.add_to_fx_list(fx_pair_transf.to_dataframe())
    fx_list.len_of_lists()
    # print(type(fx_list))


fx_list.list_concacenate('fx')
fx_combined_df = fx_list.return_df().copy()
print(fx_combined_df.head())
print(type(fx_combined_df))


symbol_bond_yield_deque = deque(["DGS10"])

# symbol_bond_yield_deque = deque([])

while len(symbol_bond_yield_deque) > 0:
    symbol_bond_yield=symbol_bond_yield_deque.popleft()
    bond_yield=Fred_request_api(symbol_bond_yield)
    bond_yield.execute_full_request()
    print(type(bond_yield))
    bond_yield_transf=bond_yield.response_from_api(bond_yield)
    bond_yield_list.add_to_bond_yield_list(bond_yield_transf.to_dataframe())

bond_yield_list.list_concacenate('bond_yield')
bond_yield_combined = bond_yield_list.return_df().copy()
print(bond_yield_combined.head())
print(type(bond_yield_combined))




symbol_pl_bond_yield_deque = deque(["10yply.b"])

while len(symbol_pl_bond_yield_deque) > 0:

    symbol_pl_bond_yield=symbol_pl_bond_yield_deque.popleft()
    pl_bond_yield=Stooq_request_api(symbol_pl_bond_yield)
    # pl_bond_yield.execute_full_request()
    print(type(pl_bond_yield))
    # pl_bond_yield_transf=pl_bond_yield.response_from_api(pl_bond_yield)
    pl_bond_yield_transf=pl_bond_yield.response_from_api(pl_bond_yield.execute_full_request())
    pl_bond_yield_list.add_to_bond_yield_list(pl_bond_yield_transf.to_dataframe())

pl_bond_yield_list.list_concacenate('bond_yield')
pl_bond_yield_combined=pl_bond_yield_list.return_df().copy()
print(pl_bond_yield_combined.head())
print(type(pl_bond_yield_combined))



#merging fx and bond yields df into one
merged_asset_class_df.df_concacenate(fx_combined_df, bond_yield_combined,pl_bond_yield_combined)
print(type(merged_asset_class_df))
print(merged_asset_class_df)

merged_asset_class_df=merged_asset_class_df.return_df()
print(type(merged_asset_class_df))
print(merged_asset_class_df.head(500))


    

# bond_yield_list.list_concacenate('bond_yield')
# bond_yield_combined = bond_yield_list.return_df().copy()
# print(bond_yield_combined.head())
# print(type(bond_yield_combined))

# #merging fx and bond yields df into one
# merged_asset_class_df.df_concacenate(fx_combined_df, bond_yield_combined)
# print(type(merged_asset_class_df))
# print(merged_asset_class_df)

# merged_asset_class_df=merged_asset_class_df.return_df()
# print(type(merged_asset_class_df))
# print(merged_asset_class_df.head(500))


















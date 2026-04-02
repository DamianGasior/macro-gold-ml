from collections import deque
from src.api_providers.common_df_merger.multiple_dataframe_transformer import (
    Multiple_df_manager,
)
from src.api_providers.twelve_data.api_request_twelve_data import (
    Underlying_twelve_data_reuquest,
)
from src.api_providers.fred.api_request_fred import Fred_request_api
from src.api_providers.stooq.api_request_stooq import Stooq_request_api
from src.pipeline.pipeline import DataPipeline


def main():

    shared_dataframes_list = Multiple_df_manager()
    shared_dataframes = Multiple_df_manager()

    symbol_fx_deque = deque(["USD/PLN", "EUR/USD","UUP","GLD", "EPOL","SPY",#"USO" ,"BNO","EWG"
                             ])
    while len(symbol_fx_deque) > 0:
        symbol_fx = symbol_fx_deque.popleft()
        provider = Underlying_twelve_data_reuquest(symbol_fx)

        pipeline = DataPipeline(
            symbol_fx,
            provider,
            dataframes_list=shared_dataframes_list,
            assets_combined_dataframes=shared_dataframes,
        )
        pipeline.run()
# "IR3TIB01USM156N","IR3TIB01PLM156N"
    symbol_bond_yield_deque = deque(["DGS10","DGS5","IRLTLT01PLM156N","CPIAUCSL",'CPHPTT01PLM659N'])
    while len(symbol_bond_yield_deque) > 0:
        symbol_fred = symbol_bond_yield_deque.popleft()
        provider = Fred_request_api(symbol_fred)

        pipeline = DataPipeline(
            symbol_fred,
            provider,
            dataframes_list=shared_dataframes_list,
            assets_combined_dataframes=shared_dataframes,
        )
        pipeline.run()

    # symbol_pl_bond_yield_deque = deque(["10YPLY.B"])
    symbol_pl_bond_yield_deque = deque([])
    while len(symbol_pl_bond_yield_deque) > 0:
        symbol_stooq = symbol_pl_bond_yield_deque.popleft()
        provider = Stooq_request_api(symbol_stooq)

        pipeline = DataPipeline(
            symbol_stooq,
            provider,
            dataframes_list=shared_dataframes_list,
            assets_combined_dataframes=shared_dataframes,
        )
        pipeline.run()

    # print(type(shared_dataframes))
    # final_df=shared_dataframes_list.list_concacenate()
    # print(type(final_df))
    # print(final_df.head())

    print(pipeline)
    print(dir(pipeline))
    print(pipeline.__dict__)
    
    dataframe_combined = pipeline.merged_dataframe
    print(type(dataframe_combined))
    print(dataframe_combined.head(15))
    dataframe_combined.rename(
        columns={
            "USD/PLN": "USD_PLN",
            "EUR/USD": "EUR_USD",
            "UUP" : "UUP",
            "GLD": "GLD",
            "EPOL" : "EPOL",
            "SPY": "SPY",
            "DGS10": "US10Y",
            # "10yply.b": "PL10Y",
            "IRLTLT01PLM156N": "PL10Y",      
            "CPIAUCSL" : "CPI_US",  
            'CPHPTT01PLM659N': 'CPI_PL',
            # "IR3TIB01USM156N":"US_3M",
            # "IR3TIB01PLM156N" : "PL_3M",
            # "EWG" : 'EWG',
            # "USO" : "WTI",
            # "BNO" : "BRENT"
        }, inplace=True
    )
    
    print(type(dataframe_combined))
    print(dataframe_combined.head()) # its empty here 

    # dataframe_combined2=pipeline.merged_dataframe
    # print(type(dataframe_combined2))
    # print(dataframe_combined2.head())


    pipeline_fe = DataPipeline()
    # pipeline_fe.run_classification_features(dataframe_combined)
    pipeline_fe.run_regression_features(dataframe_combined)


if __name__ == "__main__":
    main()

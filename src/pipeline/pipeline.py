from .base_api_request import BaseAPIProvider
from .base_single_transformer import BaseDataTransformer
from src.api_providers.common_df_merger.multiple_dataframe_transformer import (
    Multiple_df_manager,
)
from src.api_providers.twelve_data.api_request_twelve_data import (
    Underlying_twelve_data_reuquest,
)
from src.api_providers.fred.api_request_fred import Fred_request_api
from src.api_providers.stooq.api_request_stooq import Stooq_request_api

dataframes_list = Multiple_df_manager()

class DataPipeline:
    def __init__(
        self,
        symbol,
        provider: BaseAPIProvider,
        data_transformer: BaseDataTransformer | None = None, # hint plus a default paramenter 
        # dataframes_list: Multiple_df_manager | None = None,
        assets_combined_dataframes: Multiple_df_manager | None = None,
        merged_asssets_dataframe: Multiple_df_manager | None = None,
    ):
        self.provider = provider
        self.data_transformer = data_transformer
        self.symbol = symbol
        self.dataframes_list = dataframes_list or Multiple_df_manager() # Value needs to be assinged to the variable , if its None it creates a new instance of  Multiple_df_manager() 
        self.assets_combined_dataframes = assets_combined_dataframes
        self.merged_asssets_dataframe = merged_asssets_dataframe

    def run(self):
        # self.provider(self.symbol)
        api_request = self.provider.execute_full_request()
        self.data_transformer: BaseDataTransformer = self.provider.response_from_api(
            api_request
        )
        print(self.data_transformer.to_dataframe())
        # self.dataframes_list.add_to_working_list(self.data_transformer.to_dataframe())
        # self.dataframes_list.list_concacenate()
        # self.assets_combined_dataframes = self.dataframes_list.return_df().copy()

        dataframes_list.add_to_working_list(self.data_transformer.to_dataframe())
        dataframes_list.list_concacenate()
        self.assets_combined_dataframes = dataframes_list.return_df().copy()

        print(self.assets_combined_dataframes.head())
        print(self.assets_combined_dataframes.tail())

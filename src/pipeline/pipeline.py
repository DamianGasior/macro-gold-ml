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


class DataPipeline:
    def __init__(
        self,
        symbol,
        provider: BaseAPIProvider,
        data_transformer :BaseDataTransformer,
        dataframes_list: Multiple_df_manager,
        assets_combined_dataframes: Multiple_df_manager,
        merged_asssets_dataframe: Multiple_df_manager,
    ):
        self.provider = provider(symbol)
        self.symbol=symbol
        self.dataframes_list = dataframes_list
        self.assets_combined_dataframes = assets_combined_dataframes
        self.merged_asssets_dataframe = merged_asssets_dataframe


    def run(self):
        data_request=self.provider(self.symbol)
        data_request.

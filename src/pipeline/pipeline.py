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
from src.ml_work.feature_engineering import FeatureEngineering
from src.ml_work.classification import Classification_model

import pandas as pd

# dataframes_list = Multiple_df_manager()



class DataPipeline:
    def __init__(
        self,
        symbol: str | None = None,
        provider: BaseAPIProvider | None = None,
        data_transformer: (
            BaseDataTransformer | None
        ) = None,  # hint plus a default paramenter
        dataframes_list: Multiple_df_manager | None = None,
        assets_combined_dataframes: Multiple_df_manager | None = None,
        merged_asssets_dataframe: Multiple_df_manager | None = None,
    ):
        self.provider = provider
        self.data_transformer = data_transformer
        self.symbol = symbol
        self.dataframes_list = (
            dataframes_list or Multiple_df_manager()
        )  # Value needs to be assinged to the variable , if its None it creates a new instance of  Multiple_df_manager()
        self._assets_combined_dataframes = assets_combined_dataframes
        # self._merged_asssets_dataframe = merged_asssets_dataframe

    @property
    def merged_dataframe(self) -> pd.DataFrame:
        return self._assets_combined_dataframes

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

        self.dataframes_list.add_to_working_list(self.data_transformer.to_dataframe())
        self.dataframes_list.list_concacenate()
        self._assets_combined_dataframes = self.dataframes_list.return_df().copy()

        print(self._assets_combined_dataframes.head())
        print(self._assets_combined_dataframes.tail())
        print(type(self._assets_combined_dataframes))
        



    
    def run_features(self,dataframe_combined):
        print('test')

        # print(self.assets_combined_dataframes.head())
        # print(self.assets_combined_dataframes.tail())
        # print(type(self.assets_combined_dataframes))

        feature_dataframe = FeatureEngineering()
        print(type(self._assets_combined_dataframes))
        # df=DataPipeline()
        # df=self.merged_dataframe
        print(type(dataframe_combined))


#napisac funkcje gdzie przekazuje dict i zmieniam nazwy w dataframe
    #     df_test.rename(
    #     columns={
    #         "USD/PLN": "USD_PLN",
    #         "EUR/USD": "EUR_USD",
    #         "DGS10": "US10Y",
    #         "10yply.b": "PL10Y"
    #     },inplace=True
    # )

        feature_dataframe.currency_features(dataframe_combined, "USD_PLN", "EUR_USD")
        print(type(feature_dataframe))
        test=feature_dataframe.fe_dataframe
        print(type(test))

        feature_dataframe.yield_spread_features(dataframe_combined,'US10Y','PL10Y')
        feature_dataframe=feature_dataframe.fe_dataframe
        print(type(feature_dataframe))
        print(feature_dataframe.tail(10))
        print(feature_dataframe.head(10))


        regression_datframe=Classification_model()
        regression_datframe.combine_dataframes(dataframe_combined,feature_dataframe)
        regression_datframe.run_random_forest_classifier()















    
    


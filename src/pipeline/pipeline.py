from collections import deque
from src.pipeline.utils import (
    SYMBOL_MAPPINGS,BASE_UNDERLYING,
    OTHER,
    VIX_SYMBOLS,
    CCY_SYMBOLS,
    RATES,
    REAL_YIELDS,
    ETF,
    RATE_DIFF,
    INFL_EXP,
    CPI,CRYPTOS
)

import pandas as pd

from src.api_providers.common_df_merger.multiple_dataframe_transformer import (
    Multiple_df_manager,
)
from src.api_providers.fred.api_request_fred import Fred_request_api
from src.api_providers.twelve_data.api_request_twelve_data import (
    Underlying_twelve_data_reuquest,
)
from src.ml_work.classification.random_forest_classification import Classification_model

# from src.api_providers.stooq.api_request_stooq import Stooq_request_api
from src.ml_work.feature_engineering.feature_engineering import FeatureEngineering
from src.ml_work.feature_engineering.feature_engineering_regression_lgbm import FeatureRegressionEngineeringLGBMR

from src.ml_work.feature_engineering.feature_engineering_regression import FeatureRegressionEngineering
from src.ml_work.regression.random_forest_regression import Regression_model
from src.ml_work.lgbm_regressor.lgbm_regression import LGBMRegressor_model
from src.ml_work.lgm_classifier.lgbm_classification import LGBMClassifier_model


from .base_api_request import BaseAPIProvider
from .base_single_transformer import BaseDataTransformer

# dataframes_list = Multiple_df_manager()


class DataPipeline:
    def __init__(
        self,
        outputsize: str | None = None,
        symbol: str | None = None,
        provider: BaseAPIProvider | None = None,
        data_transformer: BaseDataTransformer | None = None,  # hint plus a default paramenter
        dataframes_list: Multiple_df_manager | None = None,
        assets_combined_dataframes: Multiple_df_manager | None = None,
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
        # print("taking the details from property")
        # print(self._assets_combined_dataframes.head(15))
        # print(type(self._assets_combined_dataframes))
        return self._assets_combined_dataframes

    def run_requests(self, symbol_deque, broker, columns, outputsize):
        shared_dataframes_list = Multiple_df_manager()
        shared_dataframes = Multiple_df_manager()

        while len(symbol_deque) > 0:
            symbol = symbol_deque.popleft()
            if broker == "twelve":
                provider = Underlying_twelve_data_reuquest(symbol)
            elif broker == "fred":
                provider = Fred_request_api(symbol)
            pipeline = DataPipeline(
                outputsize=outputsize,
                symbol=symbol,
                provider=provider,
                dataframes_list=shared_dataframes_list,
                assets_combined_dataframes=shared_dataframes,
            )
            pipeline.run_api_requests(columns)

        return shared_dataframes_list.return_df

    def run_api_requests(self, columns):
        api_request = self.provider.execute_full_request()
        self.data_transformer: BaseDataTransformer = self.provider.response_from_api(api_request)
        self._assets_combined_dataframes = self.dataframes_list.multiple_df_manager_pipeline(
            self.data_transformer.to_dataframe()
        )
        print('symbol_processing:',self.symbol)
        self._assets_combined_dataframes = self.dataframes_list.return_df
        print(type(self._assets_combined_dataframes))
        print((self._assets_combined_dataframes.tail(10)))
        self._assets_combined_dataframes = Multiple_df_manager.rename_columns_in_df(
            self._assets_combined_dataframes, columns
        )
        return self._assets_combined_dataframes


    def run_pipeline(self):

        def req_details(size_twelve, size_fred):

            symbol_td_deque = deque(["GLD", "SPY", "USO", "BNO", "BTC/USD"])  # "EWG"
            twelve_req = DataPipeline()
            twelve_req = self.run_requests(symbol_td_deque, "twelve", SYMBOL_MAPPINGS, size_twelve)

            symbol_fred_deque = deque(
                [
                           "DEXUSEU",
                    # "DEXCHUS",
                    "DEXUSUK",
                    "DEXSZUS",
                    # "DEXHKUS",
                    "DEXJPUS",
                    "DEXSDUS","DEXCAUS",
                    # "DGS10",
                    # "DGS5",
                    # "REAINTRATREARAT10Y",
                    # "IR3TIB01USM156N",
                    # "CPIAUCSL",
                    # "WALCL",
                    "VIXCLS",
                    # "GVZCLS",
                    # "VXVCLS",
                    # "OVXCLS",
                    # "VXTYN",
                    # "AAAFF",
                    # "T10Y2Y",
                    # "T10Y3M",
                    # "T5YFF",
                    # "EXPINF1YR",
                    # "EXPINF2YR",
                    # "EXPINF5YR",
                    # "EXPINF10YR"             
                ]
            )
            fred_req = DataPipeline()
            fred_req = self.run_requests(symbol_fred_deque, "fred", SYMBOL_MAPPINGS, size_fred)

            return twelve_req, fred_req

        # request for historical datagit
        size_twelve_data = 5000
        size_fred = 100000
        twelve_req, fred_req = req_details(size_twelve_data, size_fred)

        # merging the two dataframes with all the prices from api providers
        general_object = Multiple_df_manager()
        general_object.multiple_df_manager_pipeline(twelve_req)
        general_object.multiple_df_manager_pipeline(fred_req)

        df_final = general_object.return_df
        # print(df_final.head(50))
        # print(df_final.tail(50))


        # this feature_dataframe_regression is for both random forest models [regression and classification]
        # feature_dataframe_regression = FeatureRegressionEngineering()
        # feature_dataframe_regression.feature_enginerring_pipeline(df_final)




        # commenting out during Classification model being turned on 
        
        # regression_datframe = Regression_model()
        # regression_datframe.regression_model_pipeline(
        #     df_final, feature_dataframe_regression.return_dataframe
        # )

        # commenting out during Regreesion LGBMR is turned on 

        # classification_dataframe=Classification_model()
        # classification_dataframe.classification_model_pipeline(
        #     df_final, feature_dataframe_regression.return_dataframe
        #     )


        # this is purely for LGBM model 
        feature_dataframe_regression_lgbmr = FeatureRegressionEngineeringLGBMR()
        feature_dataframe_regression_lgbmr.feature_enginerring_pipeline(df_final)

        # regression_datframe_lgbmr = LGBMRegressor_model()
        # regression_datframe_lgbmr.regression_model_pipeline( feature_dataframe_regression_lgbmr.return_dataframe)


        classificaation_datframe_lgbmr = LGBMClassifier_model()
        classificaation_datframe_lgbmr.classification_model_pipeline( feature_dataframe_regression_lgbmr.return_dataframe)

        

def run_pipeline():
    return DataPipeline().run_pipeline()

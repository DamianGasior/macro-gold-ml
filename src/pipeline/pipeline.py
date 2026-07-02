from collections import deque
from src.pipeline.utils import SYMBOL_MAPPINGS, TWELVE_DATA, FRED
import logging

import pandas as pd

from src.api_providers.common_df_merger.multiple_dataframe_transformer import (
    Multiple_df_manager,
)
from src.api_providers.fred.api_request_fred import Fred_request_api
from src.api_providers.twelve_data.api_request_twelve_data import (
    Underlying_twelve_data_reuquest,
)

from src.ml_work.feature_engineering.feature_engineering_regression_lgbm import (
    FeatureRegressionEngineeringLGBMR,
)
from src.ml_work.lgm_classifier.lgbm_classification import LGBMClassifier_model
from .base_api_request import BaseAPIProvider
from .base_single_transformer import BaseDataTransformer

logger = logging.getLogger(__name__)


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
        )  # if None, creates a new Multiple_df_manager() instance
        self._assets_combined_dataframes = assets_combined_dataframes
        # self._merged_asssets_dataframe = merged_asssets_dataframe

    @property
    def assets_combined_dataframes(self) -> pd.DataFrame:
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

        return shared_dataframes_list.df

    def run_api_requests(self, columns):
        api_request = self.provider.execute_full_request()
        self.data_transformer: BaseDataTransformer = self.provider.response_from_api(api_request)
        self._assets_combined_dataframes = self.dataframes_list.multiple_df_manager_pipeline(
            self.data_transformer.to_dataframe()
        )
        print("symbol_processing:", self.symbol)
        self._assets_combined_dataframes = self.dataframes_list.df
        print(type(self._assets_combined_dataframes))
        print((self._assets_combined_dataframes.tail(10)))
        self._assets_combined_dataframes = Multiple_df_manager.rename_columns_in_df(
            self._assets_combined_dataframes, columns
        )
        return self._assets_combined_dataframes

    def run_pipeline(self):

        def req_details(size_twelve, size_fred):

            symbol_td_deque = deque(TWELVE_DATA)  # "EWG"
            twelve_req = DataPipeline()
            twelve_req = self.run_requests(symbol_td_deque, "twelve", SYMBOL_MAPPINGS, size_twelve)

            symbol_fred_deque = deque(FRED)
            fred_req = DataPipeline()
            fred_req = self.run_requests(symbol_fred_deque, "fred", SYMBOL_MAPPINGS, size_fred)

            return twelve_req, fred_req

        # request for historical datagit
        size_twelve_data = 5000
        size_fred = 100000
        twelve_req, fred_req = req_details(size_twelve_data, size_fred)

        # merging the two dataframes with all the prices from api providers
        general_object = Multiple_df_manager()
        logger.debug(f"df_final head td :{twelve_req.head(10)}")
        logger.debug(f"df_final tail td :{twelve_req.tail(10)}")

        logger.debug(f"df_final head fred :{fred_req.head(10)}")
        logger.debug(f"df_final tail fred :{fred_req.tail(10)}")

        general_object.multiple_df_manager_pipeline(twelve_req)
        general_object.multiple_df_manager_pipeline(fred_req)
        # fred has missing data, need to check which one exactly
        df_final = general_object.df

        # this is purely for LGBM model
        feature_dataframe_regression_lgbmr = FeatureRegressionEngineeringLGBMR()
        feature_dataframe_regression_lgbmr.feature_enginerring_pipeline(df_final)

        # regression_datframe_lgbmr = LGBMRegressor_model()
        # regression_datframe_lgbmr.regression_model_pipeline( feature_dataframe_regression_lgbmr.return_dataframe)

        classificaation_datframe_lgbmr = LGBMClassifier_model()
        classificaation_datframe_lgbmr.classification_model_pipeline(
            feature_dataframe_regression_lgbmr.df
        )
        classificaation_datframe_lgbmr.save_model()


def run_pipeline():
    return DataPipeline().run_pipeline()

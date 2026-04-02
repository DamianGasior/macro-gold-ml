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
from src.ml_work.feature_engineering_regression import FeatureRegressionEngineering
from src.ml_work.classification import Classification_model
from src.ml_work.regression import Regression_model
from src.ml_work.trading_estimates import Trading_venue


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
        print('taking the details from property')
        print(self._assets_combined_dataframes.head(15))
        return self._assets_combined_dataframes

    def run(self):
        api_request = self.provider.execute_full_request()
        self.data_transformer: BaseDataTransformer = self.provider.response_from_api(
            api_request
        )


        self._assets_combined_dataframes=self.dataframes_list.multiple_df_manager_pipeline(self.data_transformer.to_dataframe())
        self._assets_combined_dataframes = self.dataframes_list.return_df



    def run_classification_features(self, dataframe_combined):

        ## this part cover Classification
        feature_dataframe = FeatureEngineering()
        feature_dataframe.feature_enginerring_pipeline(
            dataframe_combined
        )  # run this feature engineering

        #    or the below

        # feature_dataframe.currency_features(
        #     dataframe_combined, "USD_PLN", "EUR_USD", "UUP", "GLD")

        # feature_dataframe.yield_spread_features(dataframe_combined, "US10Y", "PL10Y")

        # feature_dataframe.etf_features(dataframe_combined, "EPOL", "SPY")

        # # feature_dataframe.etf_ccy_features('USD_PLN','EPOL','SPY')

        # feature_dataframe.correlation_betwee_instrumentss(
        #     "USD_PLN", "EUR_USD", "UUP", "GLD",  "EPOL", "SPY")

        feature_dataframe = feature_dataframe.fe_dataframe

        # Random Forest pipeline
        classification_datframe = Classification_model()

        classification_datframe.combine_dataframes(
            dataframe_combined, feature_dataframe
        )
        classification_datframe.set_train_test_split()
        # classification_datframe.multiple_random_forest_combinations()
        model_random_forest, y_pred_rd_forest = (
            classification_datframe.run_random_forest_classifier()
        )
        classification_datframe.feature_importnace(model_random_forest)
        classification_datframe.evaluate_segments(model_random_forest)
        classification_datframe.different_params_setup(
            model_random_forest, y_pred_rd_forest
        )
        classification_datframe.confusion_matrix_graph(
            y_pred_rd_forest, "random_forest"
        )
        classification_datframe.histogram_result("random_forest", model_random_forest)

        # classification_datframe_splits=Classification_model()
        # classification_datframe_splits.combine_dataframes(dataframe_combined,feature_dataframe)
        # classification_datframe_splits.pipeline_with_time_series_split()

        # Xgboost
        # classification_datframe_xgboost = Classification_model()
        # classification_datframe_xgboost.combine_dataframes(
        #     dataframe_combined, feature_dataframe
        # )
        # classification_datframe_xgboost.set_train_test_split()
        # model_xboost, y_pred_xgboost = classification_datframe_xgboost.run_xgboost_model()
        # classification_datframe_xgboost.evaluate_segments(model_xboost)
        # classification_datframe_xgboost.different_params_setup(model_xboost, y_pred_xgboost)
        # classification_datframe_xgboost.confusion_matrix_graph(y_pred_xgboost, "xgboost")

    def run_regression_features(self, dataframe_combined):

        feature_dataframe_regression = FeatureRegressionEngineering()
        feature_dataframe_regression.feature_enginerring_pipeline(dataframe_combined)

        feature_dataframe_regression = feature_dataframe_regression.fe_dataframe

        regression_datframe = Regression_model()
        # regression_datframe.regression_time_split_model_pipeline(dataframe_combined,feature_dataframe_regression)
        regression_datframe.regression_model_pipeline(
            dataframe_combined, feature_dataframe_regression
        )

        # trading_model = Trading_venue()
        # trading_model.predict_and_threshold(
        #     regression_datframe.return_X_train, regression_datframe.return_model_f_reg
        # )

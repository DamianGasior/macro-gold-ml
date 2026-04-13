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
from src.ml_work.classification import Classification_model

# from src.api_providers.stooq.api_request_stooq import Stooq_request_api
from src.ml_work.feature_engineering import FeatureEngineering
from src.ml_work.feature_engineering_regression import FeatureRegressionEngineering
from src.ml_work.regression import Regression_model
from src.ml_work.trading_estimates import Trading_venue
from src.ml_work.backtest import Backtest

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

    def run_classification_features(self, dataframe_combined):

        ## this part cover Classification
        feature_dataframe = FeatureEngineering()
        feature_dataframe.feature_enginerring_pipeline(dataframe_combined)

        # run this feature engineering

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

        classification_datframe.combine_dataframes(dataframe_combined, feature_dataframe)
        classification_datframe.set_train_test_split()
        # classification_datframe.multiple_random_forest_combinations()
        model_random_forest, y_pred_rd_forest = (
            classification_datframe.run_random_forest_classifier()
        )
        classification_datframe.feature_importnace(model_random_forest)
        classification_datframe.evaluate_segments(model_random_forest)
        classification_datframe.different_params_setup(model_random_forest, y_pred_rd_forest)
        classification_datframe.confusion_matrix_graph(y_pred_rd_forest, "random_forest")
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

        feature_dataframe_regression = FeatureRegressionEngineering()
        feature_dataframe_regression.feature_enginerring_pipeline(df_final)

        regression_datframe = Regression_model()
        regression_datframe.regression_model_pipeline(
            df_final, feature_dataframe_regression.return_dataframe
        )

        # print(regression_datframe.return_combined_dataframe['equity_curve'])

        # request for latest 120 bd /snapshot data
        # size_twelve_data=120
        # size_fred=120
        # twelve_req_latest,fred_req_latest=req_details(size_twelve_data,size_fred)

        # general_object_latest=Multiple_df_manager()
        # general_object_latest.multiple_df_manager_pipeline(twelve_req_latest)
        # general_object_latest.multiple_df_manager_pipeline(fred_req_latest)

        # df_final_latest=general_object_latest.return_df

        # feature_dataframe_regression_latest = FeatureRegressionEngineering()
        # feature_dataframe_regression_latest.feature_enginerring_pipeline(df_final_latest)

        # regression_datframe_latest = Regression_model()
        # regression_datframe_latest.combine_dataframes(df_final_latest, feature_dataframe_regression_latest.return_dataframe)

        # trading_model = Trading_venue()
        # trading_model.trading_pipeline(regression_datframe.return_X_train, regression_datframe.return_model_f_reg, regression_datframe.return_x ,regression_datframe.return_y_pred)
        # trading_model.trading_pipeline(regression_datframe.return_y_pred, regression_datframe.return_model_f_reg, regression_datframe.return_x )

        # trading_model_backtest = Backtest()
        # trading_model_backtest.trading_pipeline(regression_datframe.return_X_train, regression_datframe.return_model_f_reg, regression_datframe.return_x )


def run_pipeline():
    return DataPipeline().run_pipeline()

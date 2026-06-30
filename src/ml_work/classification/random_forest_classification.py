import logging
import os
from src.pipeline import utils
from src.api_providers.common_df_merger.multiple_dataframe_transformer import (
    Multiple_df_manager,
)
from src.ml_work import financial_metrics
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

pd.set_option("display.max_rows", 200)  # więcej niż 150
pd.set_option("display.max_columns", None)  # wszystkie kolumny
pd.set_option("display.width", None)  # brak łamania linii

# from feature_engineering import FeatureEngineering
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    root_mean_squared_error,
)
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit, train_test_split

current_dir = os.path.dirname(__file__)

logger = logging.getLogger(__name__)

horizon = 21


class Classification_model:
    def __init__(self):
        self._combined_dataframe = pd.DataFrame()
        self._x = pd.DataFrame()
        self._y = pd.DataFrame()
        self._X_train = pd.DataFrame()
        self._X_test = pd.DataFrame()
        self._y_train = pd.DataFrame()
        self._y_test = pd.DataFrame()
        self._model_forest_class: RandomForestRegressor | None = None
        self._proba: np.ndarray | None = None

    @property
    def combined_dataframe(self) -> pd.DataFrame():
        return self._combined_dataframe

    @property
    def X_train(self):
        return self._X_train

    @property
    def y_train(self):
        return self._y_train

    @property
    def x(self):
        return self._x

    @property
    def model_forest_class(self):
        return self._model_forest_class

    def combine_dataframes(self, raw_data_df, feature_df):
        raw_data_df_normalized = Multiple_df_manager.normalize_df(raw_data_df)
        feature_df_normalized = Multiple_df_manager.normalize_df(feature_df)

        self._combined_dataframe = feature_df_normalized.join(
            raw_data_df_normalized[["GOLD"]], how="inner"
        )  # merging two df's  by dates, mathcing to dates in feature.df dataframe.
        # print(type(self._combined_dataframe))
        logging.debug(self._combined_dataframe.head(14))
        self._combined_dataframe = self._combined_dataframe.sort_index()

        future_return = (
            self._combined_dataframe["GOLD"].shift(-horizon) / self._combined_dataframe["GOLD"] - 1
        )  # shifting the data by  horizon days and calc the return
        self._combined_dataframe["moved_price"] = self._combined_dataframe["GOLD"].shift(-horizon)
        self._combined_dataframe["target_pct"] = future_return

        self._combined_dataframe["GOLD_daily_return"] = self._combined_dataframe[
            "GOLD"
        ].pct_change()

        print(self._combined_dataframe["target_pct"])

        print(type(future_return))
        print(future_return.head(50))
        print(future_return.tail(50))

        min_future_return = future_return.min()
        max_future_return = future_return.max()
        print(f"min_future_return is : {min_future_return}")
        print(f"max_future_return is : {max_future_return}")

        q_low = future_return.quantile(0.3)
        print(f"Lower quantile is :{q_low}")
        median = future_return.quantile(0.5)
        print(f"Median quantile is :{median}")
        q_high = future_return.quantile(0.7)
        print(f"Higher quantile is :{q_high}")

        self._combined_dataframe["target"] = 1
        self._combined_dataframe.loc[future_return <= q_low, "target"] = 0  # down
        self._combined_dataframe.loc[future_return >= q_high, "target"] = 2  # up

        # self._combined_dataframe["target"] = 0 # no trade
        # # self._combined_dataframe.loc[future_return <= q_low, "target"] = 0  # down
        # self._combined_dataframe.loc[future_return > q_high, "target"] =   # up

        # self._combined_dataframe["target"] = future_return

        self._combined_dataframe = self._combined_dataframe.dropna(
            subset=[
                "target",
                "target_pct",
                "moved_price",
            ]
        )  # removing only those rows where target and 'target_pct' is NaN
        # print(self._combined_dataframe.isna().sum())
        # print(self._combined_dataframe["target"].value_counts())

        self._x = self._combined_dataframe.drop(
            columns=["target", "GOLD", "target_pct", "moved_price", "GOLD_daily_return"]
        )  # droppoing the selected columns, matrix with features
        self._y = self._combined_dataframe["target"]  # leaving selected columns df with target
        # logging.info(
        #     f"\nClass balance/distribution/proportion of the target is: {self._y.value_counts(normalize=True)}" # counts how much in percentage there are results with '0' , how much with results '1'
        # )
        # print(self._combined_dataframe[["target", "GOLD", "target_pct", "moved_price"]].head(50))

        assert self._x.index.equals(self._y.index)
        return self._combined_dataframe

    def feature_importnace(self):

        importance = self._model_forest_class.feature_importances_
        df_imp = pd.DataFrame(
            {"feature": self._X_train.columns, "importance": importance}
        ).sort_values(by="importance", ascending=False)
        print(df_imp.head(150))
        cumsum = df_imp["importance"].cumsum()
        print(f"Cumsum results : \n {cumsum.head(150)}")

    def set_train_test_split(self):
        self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(
            self._x, self._y, test_size=0.2, shuffle=False
        )

    def run_random_forest_classification(self):

        model = RandomForestClassifier(
            n_estimators=300,  # liczba drzew
            max_depth=3,  # płytkie drzewa = mniej overfittingu
            min_samples_leaf=10,  # wygładza predykcje
            max_features="sqrt",  # losowość → lepsza generalizacja
            random_state=42,
            n_jobs=-1,
        )
        print(
            f"""
        Model name is :  {type(model).__name__},
        model details are: {model.get_params()}"""
        )

        assert len(self._X_train) == len(
            self._y_train
        ), "self._X_train and self._y_train do not have the same lenght"

        self._model_forest_class = model.fit(self._X_train, self._y_train)
        proba = self._model_forest_class.predict_proba(self._X_test)[:, :]
        # pick up all the line, but only the second column, which is the one for class 1

        # numpy slicing
        # [:, :]  → wszcopy all  (without any changes)
        # [:, 1]  → one column  ( target score)
        # [1, :]  → one row

        # print(type(proba))
        # print(len(proba))
        self._proba = proba
        # print(proba)

        print(f"proba.min:{proba.min()}")
        print(f"proba.max: {proba.max()}")

    def backtest_strategy(self):

        self._combined_dataframe[["proba_down", "proba_up", "proba_neutral"]] = np.nan
        self._combined_dataframe.loc[self._X_test.index, "proba_up"] = self._proba[
            :, 2
        ]  # assigning only those results, based on index from _x_test
        self._combined_dataframe.loc[self._X_test.index, "proba_down"] = self._proba[
            :, 0
        ]  # assigning only those results, based on index from _x_test
        self._combined_dataframe.loc[self._X_test.index, "proba_neutral"] = self._proba[
            :, 1
        ]  # assigning only those results, based on index from _x_test

        mask = self._combined_dataframe[
            "proba_up"
        ].notna()  # will be used for index where the value is not na
        self._combined_dataframe["score"] = (
            self._combined_dataframe["proba_up"] - self._combined_dataframe["proba_down"]
        )
        trade = self._combined_dataframe["score"].quantile(0.8)
        print(trade)
        self._combined_dataframe.loc[mask, "rank"] = self._combined_dataframe.loc[
            mask, "score"
        ].rank(pct=True)
        self._combined_dataframe["position"] = 0  # assigning by default all values to 0
        self._combined_dataframe.loc[self._combined_dataframe["rank"] > 0.8, "position"] = 1
        self._combined_dataframe.loc[self._combined_dataframe["rank"] < 0.2, "position"] = -1

        # self._combined_dataframe[["proba_up","proba_neutral"]] = np.nan
        # self._combined_dataframe.loc[self._X_test.index, "proba_up"] = self._proba[:,1]  # assigning only those results, based on index from _x_test
        # # self._combined_dataframe.loc[self._X_test.index, "proba_down"] = self._proba[:,0]  # assigning only those results, based on index from _x_test
        # self._combined_dataframe.loc[self._X_test.index, "proba_neutral"] = self._proba[:,0]

        # mask = self._combined_dataframe["proba_up"].notna()  # will be used for index where the value is not na
        # self._combined_dataframe['score'] = self._combined_dataframe["proba_up"] - self._combined_dataframe["proba_neutral"]
        # self._combined_dataframe.loc[mask,'rank'] = self._combined_dataframe.loc[mask,"score"].rank(pct=True)
        # self._combined_dataframe["position"] = 0  # assigning by default all values to 0
        # self._combined_dataframe.loc[self._combined_dataframe['rank'] > 0.9,'position'] = 1
        # self._combined_dataframe.loc[self._combined_dataframe['rank'] < 0.1,'position'] = -1

        self._combined_dataframe["strategy_return"] = (
            self._combined_dataframe["position"].shift(1) * self._combined_dataframe["target_pct"]
        )
        self._combined_dataframe["equity_curve"] = (
            1 + self._combined_dataframe["strategy_return"]
        ).cumprod()
        print(self._combined_dataframe["strategy_return"])
        returns = self._combined_dataframe["strategy_return"].dropna()
        print(self._combined_dataframe["strategy_return"])
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
        print("Share ratio (annualized) is : ", sharpe)

        years = (
            self._combined_dataframe.index.max().year - self._combined_dataframe.index.min().year
        )
        retunrs_trades = returns[returns != 0].dropna()
        n_trades = len(retunrs_trades) / years
        print(f"\n number of returns higher than 0 : {retunrs_trades.count()}")
        print("number of returns equla to 0 : ", (returns == 0).sum())
        sharpe_trade = (retunrs_trades.mean() / retunrs_trades.std()) * np.sqrt(n_trades)
        print("Sharpe non zero ratio (considering trades) is : ", sharpe_trade)

        rolling_sh_feat = 10
        sharpe_roll = (
            returns.rolling(rolling_sh_feat).mean() / returns.rolling(rolling_sh_feat).std()
        ).dropna()
        print(f"Rolling sharpe  ratio of roll {rolling_sh_feat} is : {sharpe_roll}")

        return self._combined_dataframe

    def evaluating_backtest_stategy(self):

        financial_metrics.calculate_cagr(self._combined_dataframe, "equity_curve")
        financial_metrics.drawdown_from_peak(self._combined_dataframe, "equity_curve")
        financial_metrics.return_std(self._combined_dataframe, "strategy_return")

        pnl_long = self._combined_dataframe[self._combined_dataframe["position"] == 1][
            "strategy_return"
        ].mean()
        pnl_short = self._combined_dataframe[self._combined_dataframe["position"] == -1][
            "strategy_return"
        ].mean()
        hit_rate = (self._combined_dataframe["strategy_return"] > 0).mean()
        average_trade_return = self._combined_dataframe["strategy_return"].mean()

        print("pnl_long : ", pnl_long)
        print("pnl_short : ", pnl_short)
        print("hit_rate : ", hit_rate)
        print("average_trade_return : ", average_trade_return)

        financial_metrics.buy_and_hold_strateg(self._combined_dataframe, "GOLD")
        financial_metrics.calculate_cagr(self._combined_dataframe, "GOLD")
        financial_metrics.drawdown_from_peak(self._combined_dataframe, "GOLD")
        financial_metrics.return_std(self._combined_dataframe, "GOLD_daily_return")

    def equity_curve_result(self):
        plt.figure(figsize=(12, 6))
        self._combined_dataframe["equity_curve"].plot()
        plt.title("Equity Curve")
        plt.xlabel("Date")
        plt.ylabel("Equity")
        plt.grid(True)
        path = os.path.join(current_dir, "equity_curve.jpg")
        plt.savefig(path)
        plt.close()

    def evaluate_segments(self):
        return None

    # def confusion_matrix_graph(self, y_prediction, name: str):
    #     plt.figure()
    #     cm_result = ConfusionMatrixDisplay.from_predictions(
    #         self._y_test,
    #         y_prediction,
    #         display_labels=["USD_PLN", "USD_PLN"],
    #         cmap="Blues",
    #     )
    #     path_boost = os.path.join(current_dir, f"{name}_confusion_matrix.png")
    #     plt.savefig(path_boost)
    #     plt.close()
    #     return cm_result

    def different_params_setup(self, model_input, pred_input):
        accuracy = accuracy_score(self._y_test, pred_input)
        print(f"accuracy_score is : {accuracy}")
        train_acc = model_input.score(self._X_train, self._y_train)  # accuracy on training data
        test_acc = model_input.score(self._X_test, self._y_test)
        print(f"Train accuracy is : {train_acc}")
        print(f"Test accuracy is : {test_acc}")
        print(f"{confusion_matrix(self._y_test, pred_input)}")
        print(f"{classification_report(self._y_test, pred_input)}")

    def multiple_random_forest_combinations(self):
        param_grid = {
            "max_depth": [2, 3, 4, 5],
            "min_samples_leaf": [3, 5, 10],
            "n_estimators": [300, 400, 500],
            "max_features": ["sqrt"],
            "random_state": [42],
        }
        rfst = RandomForestRegressor()
        tscv = TimeSeriesSplit(n_splits=5)
        grid = GridSearchCV(rfst, param_grid, cv=tscv, scoring="r2", n_jobs=-1)

        print(f"""model details are: {rfst}""")

        grid.fit(self._X_train, self._y_train)
        print(
            f"""grid.best_params_ : {grid.best_params_}
            grid.best_score_: {grid.best_score_}"""
        )

        best_model = grid.best_estimator_

        y_pred = best_model.predict(self._X_test)

        train_r2 = best_model.score(self._X_train, self._y_train)
        test_r2 = best_model.score(self._X_test, self._y_test)

        print(f"Train R2: {train_r2}")
        print(f"Test R2 : {test_r2}")

    def pipeline_with_time_series_split(self):
        tscv = TimeSeriesSplit(n_splits=5)
        count = 0
        print("Start of the TimeSeriesSplit split : 5  ")

        for train_idx, test_idx in tscv.split(self._x):
            # print(f'count print {count}')
            count = count + 1
            print(f"TimeSeriesSplit split : {count}")
            # print(f'count print {count}')

            self._X_train, self._X_test = (
                self._x.iloc[train_idx],
                self._x.iloc[test_idx],
            )

            self._y_train, self._y_test = (
                self._y.iloc[train_idx],
                self._y.iloc[test_idx],
            )
            # print(self._X_train)
            # print(self._X_test)
            # print(self._y_train)
            # print(self._y_test)

            self.run_random_forest_regression()
            self.evaluate_segments()
            # self.feature_importnace()

        print("End of the TimeSeriesSplit")

    def classification_model_pipeline(self, raw_dataframe, feat_dataframe):
        raw_dataframe = utils.clean_features(raw_dataframe)
        feat_dataframe = utils.clean_features(feat_dataframe)

        self.combine_dataframes(raw_dataframe, feat_dataframe)

        self.set_train_test_split()
        self.run_random_forest_classification()
        self.backtest_strategy()
        self.evaluating_backtest_stategy()
        # self.evaluate_segments()
        self.feature_importnace()
        self.equity_curve_result()

    def regression_time_split_model_pipeline(self, raw_dataframe, feat_dataframe):
        self.combine_dataframes(raw_dataframe, feat_dataframe)
        self.pipeline_with_time_series_split()
        # self.feature_importnace()

        # print(type(threshold_top))
        # print(f'threshold_top : {threshold_top}')
        # print(f'threshold_bottom : {threshold_bottom}')
        # # print(self._y_pred)
        # print(f'_y_pred : {self._y_pred[0]}')

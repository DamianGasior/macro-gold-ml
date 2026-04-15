import logging
import os
from src.pipeline import utils
from src.api_providers.common_df_merger.multiple_dataframe_transformer import (
    Multiple_df_manager,
)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt


pd.set_option("display.max_rows", 200)  # więcej niż 150
pd.set_option("display.max_columns", None)  # wszystkie kolumny
pd.set_option("display.width", None)  # brak łamania linii

# from feature_engineering import FeatureEngineering
from lightgbm import LGBMRegressor
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class LGBMRegressor:
    def __init__(self):
        self._combined_dataframe = pd.DataFrame()
        self._x = pd.DataFrame()
        self._y = pd.DataFrame()
        self._X_train = pd.DataFrame()
        self._X_test = pd.DataFrame()
        self._y_train = pd.DataFrame()
        self._y_test = pd.DataFrame()
        self._y_pred: np.ndarray | None = None
        self._lgbm_model: LGBMRegressor | None = None

    @property
    def return_combined_dataframe(self) -> pd.DataFrame():

        return self._combined_dataframe

    @property
    def return_X_train(self):
        return self._X_train

    @property
    def return_y_train(self):
        return self._y_train

    @property
    def return_x(self):
        return self._x

    @property
    def return_y_pred(self):
        return self._y_pred

    @property
    def return_model_f_reg(self):
        return self._model_forest_reg

    def combine_dataframes(self, raw_data_df, feature_df):
        raw_data_df_normalized = Multiple_df_manager.normalize_df(raw_data_df)
        feature_df_normalized = Multiple_df_manager.normalize_df(feature_df)

        self._combined_dataframe = feature_df_normalized.join(
            raw_data_df_normalized[["GOLD"]], how="inner"
        )  # merging two df's  by dates, mathcing to dates in feature.df dataframe.
        # print(type(self._combined_dataframe))
        logging.debug(self._combined_dataframe.head(14))
        self._combined_dataframe = self._combined_dataframe.sort_index()

        horizon = 30
        future_return = (
            self._combined_dataframe["GOLD"].shift(-horizon) / self._combined_dataframe["GOLD"] - 1
        )  # shifting the data by  horizon days and calc the return
        self._combined_dataframe["moved_price"] = self._combined_dataframe["GOLD"].shift(-horizon)
        self._combined_dataframe["target_pct"] = future_return

        print(self._combined_dataframe["target_pct"].describe())

        print(self._combined_dataframe["target_pct"].head())


        # q_low = future_return.quantile(0.3)
        # q_high = future_return.quantile(0.7)

        self._combined_dataframe["target"] = future_return
        # self._combined_dataframe.loc[future_return <= q_low, "target"] = 0  # down
        # self._combined_dataframe.loc[future_return >= q_high, "target"] = 2  # up

        # self._combined_dataframe["target"] = (future_return >0).astype(int) # considering only the 40% top returns

        self._combined_dataframe = self._combined_dataframe.dropna(
            subset=["target", "target_pct", "moved_price"]
        )  # removing only those rows where target and 'target_pct' is NaN
        print(self._combined_dataframe.isna().sum())
        print(self._combined_dataframe["target"].value_counts())

        self._x = self._combined_dataframe.drop(
            columns=["target", "GOLD", "target_pct", "moved_price"]
        )  # droppoing the selected columns, matrix with features
        self._y = self._combined_dataframe["target"]  # leaving selected columns df with target
        # logging.info(
        #     f"\nClass balance/distribution/proportion of the target is: {self._y.value_counts(normalize=True)}" # counts how much in percentage there are results with '0' , how much with results '1'
        # )
        print(self._combined_dataframe[["target", "GOLD", "target_pct", "moved_price"]].head(50))

        assert self._x.index.equals(self._y.index)

        return self._combined_dataframe

    def feature_importnace(self):

        importance = self._model_forest_reg.feature_importances_
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

    def run_random_forest_regression(self):

        model = LGBMRegressor(
            n_estimators=300,  # liczba drzew
            max_depth=3,  # płytkie drzewa = mniej overfittingu
            num_leaves=15, 
            learning_rate=0.05,
            random_state=42,
            n_jobs=-1,
        )
        print(
            f"""
        Model name is :  {type(model).__name__},
        model details are: {model.get_params()}"""
        )

        mask = ~np.isfinite(self._X_train.to_numpy())

        print("INF/NAN count:", mask.sum())
        print(self._X_train.columns[mask.any(axis=0)])

        self._lgbm_model = model.fit(self._X_train, self._y_train)
        y_pred = self._lgbm_model.predict(self._X_test)
        print(y_pred.shape)
        self._y_pred = y_pred
        # print(self._y_pred)

        corr = np.corrcoef(y_pred, self._y_test)[0, 1]
        print("corr:", corr)
        print(
            "if corr < 0 , model is inverted(prediction up and target down and vice versa); if corr > 0 , then model works as a classical model(  pred  up and target up ; pred down and target down )"
        )

        # print(np.unique(self._y))  # returns [ 0 1]
        # print(np.unique(self._model_forest_reg.predict(self._x)))  # returns [0.20141806 0.20218758 0.20556417 ... 0.81441768 0.81523677 0.82363257], retuns probabilities

        return y_pred

    def backtest_strategy(self):

        self._combined_dataframe["predicted_signal"] = np.nan  # assigningn nan to the whole column
        self._combined_dataframe.loc[self._X_test.index, "predicted_signal"] = (
            self._y_pred
        )  # assigning only those results, based on index from _x_test

        mask = self._combined_dataframe[
            "predicted_signal"
        ].notna()  # will be used for index where the value is not na
        threshold_top = self._combined_dataframe.loc[mask, "predicted_signal"].quantile(0.7)
        threshold_bottom = self._combined_dataframe.loc[mask, "predicted_signal"].quantile(0.3)

        self._combined_dataframe["position"] = 0  # assigning by default all values to 0
        self._combined_dataframe.loc[mask & (self._combined_dataframe['predicted_signal'] > threshold_top ),'position'] = 1
        self._combined_dataframe.loc[mask & (self._combined_dataframe['predicted_signal'] < threshold_bottom ),'position'] = -1

 
        years=self._combined_dataframe.index.max().year - self._combined_dataframe.index.min().year
        print(years)
  

        # print(self._combined_dataframe["predicted_signal"].describe())
        # print(self._combined_dataframe["predicted_signal"].isna().sum())
        # test_print = self._combined_dataframe["predicted_signal"].notna() & (
        #     self._combined_dataframe["predicted_signal"] != 0
        # )
        # print(test_print.value_counts().head(20))
        # print(test_print.sum().head(20))

        self._combined_dataframe["strategy_return"] = (
            self._combined_dataframe["position"].shift(1) * self._combined_dataframe["target_pct"]
        )
        self._combined_dataframe["equity_curve"] = (
            1 + self._combined_dataframe["strategy_return"]
        ).cumprod()
        # print(self._combined_dataframe["equity_curve"])
        # print(self._combined_dataframe["equity_curve"].value_counts())
        # print(self._combined_dataframe[["position", "target", "strategy_return"]].head(20))
        # print(self._combined_dataframe["strategy_return"].sum())
        # print(self._combined_dataframe["strategy_return"].abs().sum())

        mask_return = self._combined_dataframe["strategy_return"].notna() & (
            self._combined_dataframe["strategy_return"] != 0
        )

       

        # print(self._combined_dataframe.loc[mask_return, "strategy_return"].head(150))
        # print("sum", self._combined_dataframe.loc[mask_return, "strategy_return"].sum())

       
        returns=self._combined_dataframe["strategy_return"].dropna()

        sharpe = ((returns.mean()/returns.std())*np.sqrt(252))
        print('Share ratio (annualized) is : ' , sharpe)


        retunrs_non_zero=returns[returns !=0].dropna()


        n_trades=len(retunrs_non_zero)
        print(f'\n number of returns higher than 0 : {retunrs_non_zero.count()}')
        print('number of returns equla to 0 : ',(returns == 0).sum())
        sharpe_non_zero_days = ((retunrs_non_zero.mean()/retunrs_non_zero.std())*np.sqrt(n_trades))/years
        # print(type(sharpe_non_zero_days))
        print('Sharpe non zero ratio (considering trades) is : ' , sharpe_non_zero_days)


        rolling_sh_feat=10
        # print(returns.isna().sum())
        sh_numerator= returns.rolling(rolling_sh_feat).mean().dropna()
        sh_denominator=returns.rolling(rolling_sh_feat).std().dropna()
        # print(sh_numerator.isna().sum())
        # print(sh_denominator.isna().sum())



        sharpe_roll = (returns.rolling(rolling_sh_feat).mean()/returns.rolling(rolling_sh_feat).std()).dropna()
        print(f'Rolling sharpe  ratio of roll {rolling_sh_feat} is : {sharpe_roll}')
        # print(self._combined_dataframe['predicted_signal','strategy_return','equity_curve'].tail(20))

        return self._combined_dataframe

    def equity_curve_result(self):
        plt.figure(figsize=(12, 6))
        self._combined_dataframe['equity_curve'].plot()
        plt.title("Equity Curve")
        plt.xlabel("Date")
        plt.ylabel("Equity")
        plt.grid(True)
        path = os.path.join(current_dir, "equity_curve.jpg")
        plt.savefig(path)
        plt.close()

    def evaluate_segments(self):

        corr = np.corrcoef(self._y_pred, self._y_test)[0, 1]
        print(
            f"""\nCorrelation is {corr}
        
        In finance : 
        correlation	meaning
        0.05-0.15	weak signal
        0.2-0.3	OK
        0.3-0.5	strong singanl ✅
        >0.5	rare / suspiciously high
        """
        )

        # parameter=0.1
        # len_of_data=len(self._y_pred)
        # k=int(parameter * len_of_data)

        # assert len(self._y_pred) == len(self._y_test), 'y_test and y_pred do not have the same lenght'

        # # print(k)
        # y_pred_sorted=np.argsort(self._y_pred)
        # # print(y_pred_sorted)

        # top_per_index = y_pred_sorted[-k:]
        # bottom_per_index = y_pred_sorted[:k]

        target_pct_test = self._combined_dataframe.loc[self._X_test.index, "target_pct"]
        # print(target_pct_test)
        assert len(target_pct_test) == len(
            self._y_test
        ), "y_test and y_pred do not have the same lenght"

        parameter = 0.3
        len_of_data = len(target_pct_test)
        k = int(parameter * len_of_data)

        # print(k)
        sortted_y_pred = np.argsort(self._y_pred)
        # print(y_pred_sorted)

        top_per_index = sortted_y_pred[-k:]
        bottom_per_index = sortted_y_pred[:k]

        top_return = target_pct_test.iloc[top_per_index].mean()
        bottom_return = target_pct_test.iloc[bottom_per_index].mean()

        print(f"Top {parameter:.2%}  avg return: {top_return}, in  pct it is :{top_return:.3%}")
        print(
            f"Bottom {parameter:.2%}  avg return:{bottom_return}, in  pct it is :{bottom_return:.3%}"
        )

        hit_rate_positive_return = (target_pct_test.iloc[top_per_index] > 0).mean()
        print(f"Hit rate for top {parameter:.2%} is {hit_rate_positive_return:.2%} ")

        hit_rate_pnegative_return = (target_pct_test.iloc[top_per_index] < 0).mean()
        print(f"Hit rate for bottom {parameter:.2%} is {hit_rate_pnegative_return:.2%} ")

        std_test = self._y_test.std()
        print(f"\ny_test std: {std_test},in  pct it is :{std_test:.3%}\n")

        mae = round(mean_absolute_error(self._y_test, self._y_pred), 6)
        mse = mean_squared_error(self._y_test, self._y_pred)
        rmse = root_mean_squared_error(self._y_test, self._y_pred)
        r2 = r2_score(self._y_test, self._y_pred)

        print(
            f"MAE test: {mae}, in  pct it is :{mae:.3%}; average model mistake vs std: {std_test:.3%}"
        )  # its not sensitive on outliers, hence the punishment on errors is not so big
        print(
            f"MSE test: {mse},in  pct it is :{mse:.3%}"
        )  # big errors are punished heavily , moslty used when big errors can be costly in the decision
        print(
            f"RMSE: ,{rmse},in  pct it is :{rmse:.3%}; how model does punish bigger mistakes, compare against  std: {std_test:.3%}"
        )  # how the model makes bad predictions /errors, where big mistakes are punished more
        print(
            f"R2 test: {r2},in  pct it is :{r2:.3%}"
        )  # not so useful here, it tells how much of it , comes form the model

        RMSE_std = rmse / std_test

        print(
            f"""RMSE_std is equal to : {RMSE_std}'
                result	meaning
        < 0.5	very good model
        ~1.0	model ≈ noise
        > 1.0	model weak"""
        )

        # directional accuracy, does the model recognize/predict the direction ( up or down)
        # 50 % is random, going above that is fine
        # direction_true = np.sign(self._y_test)
        # direction_pred = np.sign(self._y_pred)
        # da=np.mean(direction_true==direction_pred)
        # print(f"\nDirection accuracy is:, {da:.3%}, which tells us if we hit correctly te direction(sign);\nremeber : 50 % is random, above that its an edge" )
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

    def regression_model_pipeline(self, raw_dataframe, feat_dataframe):
        raw_dataframe = utils.clean_features(raw_dataframe)
        feat_dataframe = utils.clean_features(feat_dataframe)

        self.combine_dataframes(raw_dataframe, feat_dataframe)

        self.set_train_test_split()
        self.run_random_forest_regression()
        self.backtest_strategy()
        self.evaluate_segments()
        self.feature_importnace()
        self.equity_curve_result()
        # self.buy_sell_singal()
        # self.multiple_random_forest_combinations()

    def regression_time_split_model_pipeline(self, raw_dataframe, feat_dataframe):
        self.combine_dataframes(raw_dataframe, feat_dataframe)
        self.pipeline_with_time_series_split()
        # self.feature_importnace()

        # print(type(threshold_top))
        # print(f'threshold_top : {threshold_top}')
        # print(f'threshold_bottom : {threshold_bottom}')
        # # print(self._y_pred)
        # print(f'_y_pred : {self._y_pred[0]}')



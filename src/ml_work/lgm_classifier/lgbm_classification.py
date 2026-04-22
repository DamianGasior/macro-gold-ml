import logging
import os
from src.pipeline import utils
from src.api_providers.common_df_merger.multiple_dataframe_transformer import (
    Multiple_df_manager,
)
from src.ml_work import financial_metrics
from sklearn.metrics import log_loss
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt

import lightgbm
print("lightgbm path:", lightgbm.__file__)

from lightgbm import LGBMRegressor,LGBMClassifier
print("LGBMRegressor:", LGBMRegressor)

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


pd.set_option("display.max_rows", 200)  # więcej niż 150
pd.set_option("display.max_columns", None)  # wszystkie kolumny
pd.set_option("display.width", None)  # brak łamania linii

# from feature_engineering import FeatureEngineering


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

horizon = 21

current_dir = os.path.dirname(__file__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class LGBMClassifier_model:
    def __init__(self):
        self._combined_dataframe = pd.DataFrame()
        self._x = pd.DataFrame()
        self._y = pd.DataFrame()
        self._X_train = pd.DataFrame()
        self._X_test = pd.DataFrame()
        self._y_train = pd.DataFrame()
        self._y_test = pd.DataFrame()
        self._proba_train: np.ndarray | None = None
        self._proba_test: np.ndarray | None = None
        self._y_pred: np.ndarray | None = None
        self._lgbm_model: LGBMClassifier | None = None

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
        return self._lgbm_model

    def combine_dataframes(self, feature_df):

        feature_df_normalized = Multiple_df_manager.normalize_df(feature_df)
        print(feature_df_normalized.columns)
        self._combined_dataframe=feature_df_normalized
        logging.debug(self._combined_dataframe.head(14))
        self._combined_dataframe = self._combined_dataframe.sort_index()
        print('lenght of the dataframe before applying dropna():',len(self._combined_dataframe))
        
        future_return = self._combined_dataframe["GOLD"].pct_change(10).shift(-10)
        future_return_top=future_return.quantile(0.7)
        future_return_bottom=future_return.quantile(0.3)

        # for longs and shorts
        # self._combined_dataframe["target"] = np.where(future_return >= future_return_top, 1,
        # np.where(future_return <= future_return_bottom, -1, np.nan))                  
         
        # for longs only 
        self._combined_dataframe["target"] = np.where(future_return >= future_return_top, 1,0) 
       



        print(self._combined_dataframe["target"].value_counts(normalize=True))


        print(self._combined_dataframe["target"].tail(10))


        self._combined_dataframe = self._combined_dataframe.dropna(subset=["target",])  # removing only those rows where target and 'target_pct' is NaN
        print('sum of na including features : \n',self._combined_dataframe.isna().sum())
        print('sum of na in target column : ',self._combined_dataframe["target"].dropna())

        self._x = self._combined_dataframe.drop(columns=["target", "GOLD"])  # droppoing the selected columns, matrix with features
        self._y = self._combined_dataframe["target"]  # leaving selected columns df with target

        print('shape of X : ',self._x.shape)
        print('shape of y : ',self._y.shape)


        print(self._combined_dataframe[["target", "GOLD"]].tail(50))
        assert self._x.index.equals(self._y.index)
        return self._combined_dataframe

    def feature_importnace(self):

        importance = self._lgbm_model.feature_importances_
        print('feature_importances_',self._lgbm_model.feature_importances_)
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
        print(self._y_test.tail(50))
       

    def run_lgmr_classifier(self):

        model = LGBMClassifier(
            max_depth=2,
            num_leaves=15,
            n_estimators=100,
            min_child_samples=100,
            subsample=0.7,
            colsample_bytree=0.7,
            reg_lambda=3,
            reg_alpha=1,
            force_col_wise='true',
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
        # proba = self._lgbm_model.predict_proba(self._X_test)[:,1]
        proba_train = self._lgbm_model.predict_proba(self._X_train)

        self._proba_train = proba_train
        print(proba_train)

        proba_test = self._lgbm_model.predict_proba(self._X_test)
        self._proba_test = proba_test

        # numpy slicing
        # [:, :]  → wszcopy all  (without any changes)
        # [:, 1]  → one column  ( target score)
        # [1, :]  → one row

        print(self._lgbm_model.classes_)

        self._y_pred = np.where(self._proba_test[:,1] > self._proba_test[:,0], 1, -1) # for longs and shorts

        # # for longs only 
        # proba = self._proba_test[:,1]
        # thr = np.quantile(self._proba_test[:,1],0.80)
        # self._y_pred = np.where(proba >= thr,1,0)

    def backtest_strategy(self):

        edge,short_quantile,long_quantile=LGBMClassifier_model.edge_method(self._proba_train)
         
        edge_test,short_quantile_test,long_quantile_test=LGBMClassifier_model.edge_method(self._proba_test)


        self._combined_dataframe.loc[self._X_test.index,'prob_edge']=edge_test

        print(self._combined_dataframe['prob_edge'] )
        self._combined_dataframe["trade_signal"]=np.nan
        self._combined_dataframe.loc[self._X_test.index,"trade_signal"]=np.where(
            self._combined_dataframe.loc[self._X_test.index,'prob_edge'] >= long_quantile,1,
            np.where(self._combined_dataframe.loc[self._X_test.index,'prob_edge'] < short_quantile ,0,0))
       
        


        self._combined_dataframe["strategy_return"] = (self._combined_dataframe["trade_signal"] * self._combined_dataframe["GOLD"].pct_change(10).shift(-10))
        self._combined_dataframe["equity_curve"] = (1 + self._combined_dataframe["strategy_return"]).cumprod()
        print(self._combined_dataframe["strategy_return"])
        returns=self._combined_dataframe["strategy_return"].dropna()
        print(self._combined_dataframe["strategy_return"])
        sharpe = ((returns.mean()/returns.std())*np.sqrt(252))
        print('Sharpe ratio (annualized) is : ' , sharpe)

        years=self._combined_dataframe.index.max().year - self._combined_dataframe.index.min().year
        retunrs_trades=returns[returns !=0].dropna()
        n_trades=len(retunrs_trades) / years
        print(f'\n number of returns higher than 0 : {retunrs_trades.count()}')
        print('number of returns equla to 0 : ',(returns == 0).sum())
        sharpe_trade= ((retunrs_trades.mean()/retunrs_trades.std())*np.sqrt(n_trades))
        print('Sharpe non zero ratio (considering trades) is : ' , sharpe_trade)

        rolling_sh_feat=10
        sharpe_roll = (returns.rolling(rolling_sh_feat).mean()/returns.rolling(rolling_sh_feat).std()).dropna()
        print(f'Rolling sharpe  ratio of roll {rolling_sh_feat} is : {sharpe_roll}')
         
        return self._combined_dataframe
    

    def evaluating_backtest_stategy(self):

        financial_metrics.calculate_cagr(self._combined_dataframe,'equity_curve')
        financial_metrics.drawdown_from_peak(self._combined_dataframe,'equity_curve')
        financial_metrics.return_std(self._combined_dataframe,'strategy_return')

                
        pnl_long=self._combined_dataframe[self._combined_dataframe["position"] == 1]["strategy_return"].mean()
        pnl_short=self._combined_dataframe[self._combined_dataframe["position"] == -1]["strategy_return"].mean()
        hit_rate=(self._combined_dataframe["strategy_return"] > 0).mean()
        average_trade_return=self._combined_dataframe["strategy_return"].mean()

        print('pnl_long : ' ,pnl_long)
        print('pnl_short : ' , pnl_short)
        print('hit_rate : ' ,hit_rate)
        print('average_trade_return : ' ,average_trade_return)

        financial_metrics.buy_and_hold_strateg(self._combined_dataframe,'GOLD')    
        financial_metrics.calculate_cagr(self._combined_dataframe,'GOLD')
        financial_metrics.drawdown_from_peak(self._combined_dataframe,'GOLD')
        financial_metrics.return_std(self._combined_dataframe,'GOLD_daily_return')


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

        target_pct_test = self._combined_dataframe.loc[self._X_test.index, "target"]
        assert len(target_pct_test) == len(
            self._y_test
        ), "y_test and y_pred do not have the same lenght"

        parameter = 0.3
        len_of_data = len(target_pct_test)
        k = int(parameter * len_of_data)

        # sorted_prob = np.argsort(self._proba)
        
        sorted_prob=self._combined_dataframe["strategy_return"].sort_values()
        print(sorted_prob)
        print(sorted_prob.value_counts())
       
        top_per_index = sorted_prob[-k:]
        bottom_per_index = sorted_prob[:k]

        # top_return = target_pct_test.iloc[top_per_index].mean()
        # bottom_return = target_pct_test.iloc[bottom_per_index].mean()

        
        top_return = top_per_index.mean()
        bottom_return = bottom_per_index.mean()

        print(top_return,bottom_return)

        print(f"Top {parameter:.2%}  avg return: {top_return}, in  pct it is :{top_return:.3%}")
        print(
            f"Bottom {parameter:.2%}  avg return:{bottom_return}, in  pct it is :{bottom_return:.3%}"
        )

        # hit_rate_positive_return = (target_pct_test.iloc[top_per_index] > 0).mean()
        # print(f"Hit rate for top {parameter:.2%} is {hit_rate_positive_return:.2%} ")

        # hit_rate_pnegative_return = (target_pct_test.iloc[top_per_index] < 0).mean()
        # print(f"Hit rate for bottom {parameter:.2%} is {hit_rate_pnegative_return:.2%} ")

        std_test = self._y_test.std()
        print(f"\ny_test std: {std_test},in  pct it is :{std_test:.3%}\n")

        
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

    def different_params_setup(self):
        accuracy = accuracy_score(self._y_test, self._y_pred)
        print(f"accuracy_score is : {accuracy}")
        train_acc = self._lgbm_model.score(self._X_train, self._y_train)  # accuracy on training data
        test_acc = self._lgbm_model.score(self._X_test, self._y_test)
        print(f"Train accuracy is : {train_acc}")
        print(f"Test accuracy is : {test_acc}")
        print(f"{confusion_matrix(self._y_test, self._y_pred)}")
        print(f"{classification_report(self._y_test, self._y_pred)}")
        # auc = roc_auc_score(self._y_test, self._proba)
        auc = roc_auc_score(self._y_test, self._proba_test[:,1])
        print("ROC AUC:", auc)
        loss = log_loss(self._y_test, self._proba_test[:,1])
        print('loss is : ',loss)

    # def multiple_random_forest_combinations(self):
    #     param_grid = {
    #         "max_depth": [2, 3, 4, 5],
    #         "num_leaves": [3, 5,7, 10],
    #         "n_estimators": [100,150,200,300, 400, 500],
    #         "min_child_samples" : [30,50,70,80,100],
    #         "subsample" : [0.7],
    #         "colsample_bytree" : [0.7],
    #        "reg_lambda" : [3],
    #         "reg_alpha" : [1],
    #         "n_jobs=" : [1],
    #         "random_state": [42]
    #     }


    #     rfst = LGBMClassifier()
    #     tscv = TimeSeriesSplit(n_splits=5)
    #     grid = GridSearchCV(rfst, param_grid, cv=tscv, scoring="r2", n_jobs=-1)

    #     print(f"""model details are: {rfst}""")

    #     grid.fit(self._X_train, self._y_train)
    #     print(
    #         f"""grid.best_params_ : {grid.best_params_}
    #         grid.best_score_: {grid.best_score_}"""
    #     )

    #     best_model = grid.best_estimator_
    #     best_model = best_model.fit(self._X_train, self._y_train)
    #     proba = best_model.predict_proba(self._X_test)[:,1]

    #     train_r2 = best_model.score(self._X_train, self._y_train)
    #     test_r2 = best_model.score(self._X_test, self._y_test)

    #     print(f"Train R2: {train_r2}")
    #     print(f"Test R2 : {test_r2}")

        
    #     self._proba = proba
    #     print(proba)
    #     # numpy slicing
    #     # [:, :]  → wszcopy all  (without any changes)
    #     # [:, 1]  → one column  ( target score)
    #     # [1, :]  → one row
    #     mediana=np.median(proba)
    #     pred=np.where(proba>mediana,1,-1)
    #     print(pred)
    #     self._y_pred=pred

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

            self.run_lgmr_classifier()
            self.backtest_strategy()
            self.evaluate_segments()
            self.different_params_setup()

        print("End of the TimeSeriesSplit")

    def classification_model_pipeline(self,  feat_dataframe):
        # raw_dataframe = utils.clean_features(raw_dataframe)
        feat_dataframe = utils.clean_features(feat_dataframe)
        self.combine_dataframes( feat_dataframe)
        self.set_train_test_split()
        self.run_lgmr_classifier()
        # self.backtest_strategy()
        # self.evaluate_segments()
        # self.feature_importnace()
        # self.equity_curve_result()
        # self.different_params_setup()
        # self.evaluating_backtest_stategy()
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

    @staticmethod
    def edge_method(proba):
        prob_short=proba[:,0]
        prob_long=proba[:,1]

        edge=prob_long-prob_short

        short_quantile= np.quantile(edge,0.15)
        long_quantile= np.quantile(edge,0.85)
        return edge,short_quantile,long_quantile



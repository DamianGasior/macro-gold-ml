import logging
import os
import joblib
import shap
from src.pipeline import utils
from src.api_providers.common_df_merger.multiple_dataframe_transformer import (
    Multiple_df_manager,
)
from src.ml_work import financial_metrics
from sklearn.metrics import log_loss, roc_auc_score
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from src.ml_work.reports.report_summary import Report_Summary
import mlflow
from ml_flow.ml_flow import (
    ml_flow__log_param,
    ml_flow__log_artifact,
    ml_flow__log_metrics,
)
from pathlib import Path

logger = logging.getLogger(__name__)

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
from sklearn.model_selection import TimeSeriesSplit, train_test_split

current_dir = os.path.dirname(__file__)


# ============================================================================
# Model Configuration Constants
# ============================================================================

# Return calculation parameters (in days)
RETURN_LOOKBACK = 10  # 10-day returns for target calculation
RETURN_FORWARD = 10  # 10-day forward-looking returns for backtesting

# Backtesting parameters
PROBABILITY_THRESHOLD = 0.70  # 70th percentile for trade signal

# Data segment analysis
TOP_BOTTOM_PERCENTILE = 0.3  # Top/bottom 30% segmentsDataFrame()


class LGBMClassifier_model:
    """
    LGBM Classification model for predicting GOLD price movements.

    This class implements a complete machine learning pipeline for binary classification
    of GOLD price movements, including data preparation, model training, backtesting,
    and performance evaluation.

    Attributes:
        _combined_dataframe (pd.DataFrame): Merged and processed feature dataframe
        _x (pd.DataFrame): Feature matrix (X)
        _y (pd.DataFrame): Target variable (y)
        _X_train, _X_test (pd.DataFrame): Train/test feature matrices
        _y_train, _y_test (pd.DataFrame): Train/test target variables
        _proba_train, _proba_test (np.ndarray): Prediction probabilities
        _y_pred (np.ndarray): Binary predictions
        _lgbm_model (LGBMClassifier): Trained LightGBM model
    """

    def __init__(self):
        self._combined_dataframe = pd.DataFrame()
        self._bt = pd.DataFrame()
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
        self._pre_data: dict[str, object] = {}

    @property
    def combined_dataframe(self) -> pd.DataFrame:
        return self._combined_dataframe

    @property
    def pre_data(self) -> dict:
        return self._pre_data

    @property
    def X_train(self):
        return self._X_train

    @property
    def X_test(self):
        return self._X_test

    @property
    def y_train(self):
        return self._y_train

    @property
    def x(self):
        return self._x

    @property
    def y_pred(self):
        return self._y_pred

    @property
    def model_f_reg(self):
        return self._lgbm_model

    def combine_dataframes(self, feature_df):
        """
        Normalize and prepare dataframes for modeling.

        Creates target variable based on 70th and 30th percentiles of GOLD returns,
        performs basic data cleaning, and splits features from target.

        Args:
            feature_df (pd.DataFrame): Raw feature dataframe

        Returns:
            pd.DataFrame: Combined dataframe with target variable
        """
        feature_df_normalized = Multiple_df_manager.normalize_df(feature_df)
        logger.debug(f"Feature columns: {feature_df_normalized.columns.tolist()}")
        self._combined_dataframe = feature_df_normalized
        logger.debug(self._combined_dataframe.head(14))
        self._combined_dataframe = self._combined_dataframe.sort_index()
        logger.info(
            f"Length of dataframe before applying dropna(): " f"{len(self._combined_dataframe)}"
        )

        future_return = self._combined_dataframe["GOLD"].pct_change(10).shift(-10)
        future_return_top = future_return.quantile(1 - TOP_BOTTOM_PERCENTILE)
        future_return_bottom = future_return.quantile(TOP_BOTTOM_PERCENTILE)

        # for longs and shorts
        # self._combined_dataframe["target"] = np.where(future_return >= future_return_top, 1,
        # np.where(future_return <= future_return_bottom, -1, np.nan))

        # for longs only
        self._combined_dataframe["target"] = np.where(future_return >= future_return_top, 1, 0)

        logger.info(
            f"Target value counts:\n{self._combined_dataframe['target'].value_counts(normalize=True)}"
        )
        logger.debug(f"Last 10 target values:\n{self._combined_dataframe['target'].tail(10)}")

        self._combined_dataframe = self._combined_dataframe.dropna(
            subset=[
                "target",
            ]
        )  # removing only those rows where target and 'target_pct' is NaN
        logger.info(f"Sum of NaN including features:\n{self._combined_dataframe.isna().sum()}")
        logger.debug(
            f"Sum of NaN in target column: {self._combined_dataframe['target'].dropna().sum()}"
        )

        self._x = self._combined_dataframe.drop(
            columns=["target", "GOLD"]
        )  # droppoing the selected columns, matrix with features
        self._y = self._combined_dataframe["target"]  # leaving selected columns df with target

        logger.info(f"Shape of X: {self._x.shape}")
        logger.info(f"Shape of y: {self._y.shape}")

        logger.debug(
            f"Last 50 rows of target and GOLD:\n{self._combined_dataframe[['target', 'GOLD']].tail(50)}"
        )
        assert self._x.index.equals(self._y.index), "X and y indices do not match"
        return self._combined_dataframe

    def feature_importance(self):
        """
        Calculate and display feature importances from trained model.

        Prints feature importance DataFrame sorted by importance in descending order
        and cumulative sum of importances.
        """
        importance = self._lgbm_model.feature_importances_
        df_imp = pd.DataFrame(
            {"feature": self._X_train.columns, "importance": importance}
        ).sort_values(by="importance", ascending=False)
        logger.info(f"Top 150 feature importances:\n{df_imp.head(150)}")
        cumsum = df_imp["importance"].cumsum()
        logger.info(f"Cumulative sum of importances:\n{cumsum.head(150)}")

    def set_train_test_split(self):
        """
        Split data into train and test sets maintaining temporal order.

        Uses 80/20 split with shuffle=False to preserve time series order.
        """
        self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(
            self._x, self._y, test_size=0.2, shuffle=False
        )
        logger.debug(f"Last 50 y_test values:\n{self._y_test.tail(50)}")

    def run_lgbm_classifier(self):
        """
        Train LightGBM classifier on training data.

        Trains model on _X_train/_y_train, generates predictions and probabilities
        for both train and test sets. Applies threshold of 0.80 quantile for final predictions.
        """
        model = LGBMClassifier(
            max_depth=2,
            num_leaves=15,
            n_estimators=100,
            min_child_samples=100,
            subsample=0.7,
            colsample_bytree=0.7,
            reg_lambda=3,
            reg_alpha=1,
            force_col_wise=True,
            n_jobs=-1,
            random_state=7,
        )

        ml_flow__log_param(model, PROBABILITY_THRESHOLD, self._X_train, self._X_test)

        logger.info(f"Model name: {type(model).__name__}")
        logger.debug(f"Model details: {model.get_params()}")

        mask = ~np.isfinite(self.X_train.to_numpy())

        logger.warning(f"INF/NAN count: {mask.sum()}")
        logger.warning(f"Columns with INF/NAN: {self.X_train.columns[mask.any(axis=0)].tolist()}")

        self._lgbm_model = model.fit(self._X_train, self._y_train)
        # proba = self._lgbm_model.predict_proba(self._X_test)[:,1]
        proba_train = self._lgbm_model.predict_proba(self._X_train)

        self._proba_train = proba_train
        logger.debug(f"Training probabilities shape: {proba_train.shape}")

        proba_test = self._lgbm_model.predict_proba(self._X_test)[:, 1]
        self._proba_test = proba_test
        logger.debug(f"Shape of  self._proba_test :\n{self._proba_test.shape}")

        # numpy slicing
        # [:, :]  → wszcopy all  (without any changes)
        # [:, 1]  → one column  ( target score)
        # [1, :]  → one row

        logger.debug(f"Model classes: {self._lgbm_model.classes_}")

        # self._y_pred = np.where(self._proba_test[:,1] > self._proba_test[:,0], 1, -1) # for longs and shorts

        # # for longs only
        thr = np.quantile(self._proba_test, PROBABILITY_THRESHOLD)
        self._y_pred = np.where(self._proba_test >= thr, 1, 0)

    def save_model(self, output_dir: str = "models"):
        """Zapisuje model i nazwy kolumn do folderu models/ w katalogu głównym projektu."""
        os.makedirs(
            output_dir, exist_ok=True
        )  # new folder will be created in the current working directory : macro-gold-ml/output_dir

        joblib.dump(self._lgbm_model, f"{output_dir}/lgbm_classifier.pkl")
        joblib.dump(self._X_train.columns.tolist(), f"{output_dir}/feature_columns.pkl")

        logger.info(f"Model zapisany: {output_dir}/lgbm_classifier.pkl")
        logger.info(f"Kolumny zapisane: {output_dir}/feature_columns.pkl")
        logger.info(f"Kolumny zapisane to : {self._X_train.columns.tolist()}")
        ml_flow__log_artifact(output_dir, "lgbm_classifier.pkl")

    def shap_evaluation(self, count=1):
        explainer = shap.TreeExplainer(
            self._lgbm_model
        )  # creating an instance of class TreeExplainer, which will be used in the line below to calculate the impact
        shap_values = explainer.shap_values(self._X_test)
        # for each row and feature its being calculated how much an impact it was on the decisions model

        print(type(shap_values))
        print(shap_values.shape)
        shap.summary_plot(
            shap_values,
            self._X_test,
            show=False,  # I do not want to see it immeadiately, it will be saved
        )
        first_date, latest_date = financial_metrics.find_start_end_date(self._X_test)
        shap_dir = os.path.join(
            current_dir, "shap_summary"
        )  # current catalog + the name of the new  folder
        os.makedirs(
            shap_dir, exist_ok=True
        )  # new folder it it does not exists, it exists, no action
        path = os.path.join(
            shap_dir, f"shap_summary_{count}_{first_date}_{latest_date}.jpg"
        )  # folder plus new files
        plt.savefig(path, bbox_inches="tight")
        plt.close()

    def backtest_strategy(self):
        """
        Generate trading signals and backtest strategy performance.
        Creates trade signals based on probability edge method, calculates strategy returns,
        equity curve, and performance metrics including Sharpe ratio (both total and trade-based).
        Returns:
            pd.DataFrame: Combined dataframe with strategy metrics and equity curve
        """
        self._combined_dataframe["prob_long"] = np.nan
        self._combined_dataframe.loc[self._X_test.index, "prob_long"] = self._proba_test

        logger.debug(
            f"self._proba_test min is :\n{self._proba_test.min()} and max is {self._proba_test.max()}"
        )

        # logger.debug(f"Last 20 probability edges:\n{self._combined_dataframe['prob_long'].tail(20)}")
        self._combined_dataframe["trade_signal"] = np.nan

        # taking the top 30 % of best singals
        self._combined_dataframe.loc[self._X_test.index, "trade_signal"] = (
            self._combined_dataframe.loc[self._X_test.index, "prob_long"]
            .rank(pct=True)
            .ge(0.7)
            .astype(int)
        )

        # nowa linia — eliminacja nakładających się pozycji
        self._combined_dataframe.loc[self._X_test.index, "trade_signal"] = (
            financial_metrics.enforce_non_overlapping_signals(
                self._combined_dataframe.loc[self._X_test.index, "trade_signal"],
                holding_period=10,
            )
        )

        self._combined_dataframe["strategy_return"] = self._combined_dataframe[
            "trade_signal"
        ].fillna(0) * self._combined_dataframe["GOLD"].pct_change(10).shift(-10)

        bt = (
            self._combined_dataframe.loc[self._X_test.index]
            .dropna(subset=["strategy_return"])
            .copy()
        )
        self._bt = bt
        overlap_days = (self._bt["trade_signal"].rolling(10).sum() > 1).sum()
        logger.debug(f"Dni z nakładającymi się sygnałami: {overlap_days} z {len(self._bt)}")
        self._bt["equity_curve"] = (1 + self._bt["strategy_return"]).cumprod()
        # logger.debug(f"Equity curve:\n{self._bt['equity_curve']}")

        returns = self._bt["strategy_return"].dropna()

        first_date, latest_date = financial_metrics.find_start_end_date(self._X_test)
        self.add_to_dict("first_date", first_date)
        self.add_to_dict("latest_date", latest_date)

        sharpe = financial_metrics.sharpe_calc(returns, 252)
        logger.info(f"Sharpe ratio (annualized): {sharpe}")
        self.add_to_dict("sharpe", sharpe)

        years = max(
            self._bt.index.max().year - self._bt.index.min().year, 1
        )  # in case the fold from timeSeriesSplit will be in the same year, yeras will be then 0
        retunrs_trades = returns[returns != 0].dropna()
        n_trades = len(retunrs_trades) / years
        logger.info(f"Number of returns higher than 0: {retunrs_trades.count()}")
        logger.info(f"Number of returns equal to 0: {(returns == 0).sum()}")

        sharpe_trade = financial_metrics.sharpe_calc(retunrs_trades, n_trades)
        logger.info(f"Sharpe non-zero ratio (considering trades): {sharpe_trade}")
        self.add_to_dict("sharpe_trade", sharpe_trade)

        rolling_sh_feat = 10
        sharpe_roll = (
            returns.rolling(rolling_sh_feat).mean() / returns.rolling(rolling_sh_feat).std()
        ).dropna()
        # logger.info(f"Rolling sharpe ratio (window={rolling_sh_feat}):\n{sharpe_roll}")

        return self._bt

    def evaluating_backtest_strategy(self):
        """
        Calculate comprehensive backtest evaluation metrics.

        Computes CAGR, drawdown, return statistics, P&L by position,
        hit rate, and buy-and-hold comparison metrics.
        """
        logger.info(
            f"Information below are for the strategy from model : {type(self._lgbm_model).__name__} "
        )

        cagr = financial_metrics.calculate_cagr(self._bt, "equity_curve")
        self.add_to_dict("cagr", cagr)

        drawdown = financial_metrics.drawdown_from_peak(self._bt, "equity_curve")
        self.add_to_dict("drawdown_from_peak", drawdown)
        ml_flow__log_metrics("strategy/drawdown_from_peak_pct", drawdown * 100)

        vol_annual = financial_metrics.return_std(self._bt, "strategy_return")
        self.add_to_dict("vol_annual", vol_annual)
        ml_flow__log_metrics("strategy/vol_annual_pct", vol_annual * 100)

        dxy_trend = financial_metrics.trend_calc(self._bt, "DXY", self._X_test)
        self.add_to_dict("dxy_trend", dxy_trend)

        gold_trend = financial_metrics.trend_calc(self._bt, "GOLD", self._X_test)
        self.add_to_dict("gold_trend", gold_trend)

        spy_trend = financial_metrics.trend_calc(self._bt, "SPY", self._X_test)
        self.add_to_dict("spy_trend", spy_trend)

        pnl_long = self._bt[self._bt["trade_signal"] == 1]["strategy_return"].mean()

        financial_metrics.dates_numbers(self._bt, "trade_signal")

        # hit_rate = (self._bt["strategy_return"] > 0).mean()
        average_trade_return = self._bt["strategy_return"].mean()

        logger.info(f"PnL Long: {pnl_long}")
        # logger.info(f"PnL Short: {pnl_short}")
        # logger.info(f"Hit Rate: {hit_rate}")
        logger.info(f"average_trade_return: {average_trade_return}")
        ml_flow__log_metrics("strategy/average_trade_return_pct", average_trade_return * 100)
        ml_flow__log_metrics("strategy/pnl_long_pct", pnl_long * 100)

        logger.debug(f"Information below are for  BUY and HOLD approach")
        bh_return = financial_metrics.buy_and_hold_strateg(self._bt, "GOLD")
        ml_flow__log_metrics("benchmark/buy_and_hold_return_pct", bh_return * 100)

        bh_cagr = financial_metrics.calculate_cagr(self._bt, "GOLD")
        ml_flow__log_metrics("benchmark/buy_and_hold_cagr_pct", bh_cagr * 100)

        bh_drawdown = financial_metrics.drawdown_from_peak(self._bt, "GOLD")
        ml_flow__log_metrics("benchmark/buy_and_hold_drawdown_pct", bh_drawdown * 100)

        bh_volatility = financial_metrics.return_std(self._bt, "GOLD_return")
        ml_flow__log_metrics("benchmark/buy_and_hold_vol_annual_pct", bh_volatility * 100)

    def equity_curve_result(self):
        """
        Generate and save equity curve visualization.

        Plots equity curve as time series and saves as JPEG image
        in the current directory.
        """
        plt.figure(figsize=(12, 6))
        self._bt["equity_curve"].plot()
        plt.title("Equity Curve")
        plt.xlabel("Date")
        plt.ylabel("Equity")
        plt.grid(True)
        equity_curve_dir = os.path.join(current_dir, "equity_curve_summary")
        os.makedirs(equity_curve_dir, exist_ok=True)
        path = os.path.join(equity_curve_dir, "equity_curve.jpg")
        plt.savefig(path)
        plt.close()

    def evaluate_segments(self):
        """
        Analyze performance across percentile segments.

        Splits test data into top 30% and bottom 30% based on strategy returns,
        calculates average returns for each segment, and prints comparative analysis.
        """
        target_pct_test = self._combined_dataframe.loc[self._X_test.index, "target"]
        assert len(target_pct_test) == len(
            self._y_test
        ), "y_test and y_pred do not have the same lenght"

        parameter = 0.3
        len_of_data = len(target_pct_test)
        k = int(parameter * len_of_data)

        # sorted_prob = np.argsort(self._proba)

        sorted_prob = self._combined_dataframe["strategy_return"].sort_values()
        # logger.debug(f"Sorted probabilities:\n{sorted_prob}")
        # logger.debug(f"Sorted probabilities value counts:\n{sorted_prob.value_counts()}")

        top_per_index = sorted_prob[-k:]
        bottom_per_index = sorted_prob[:k]

        # top_return = target_pct_test.iloc[top_per_index].mean()
        # bottom_return = target_pct_test.iloc[bottom_per_index].mean()

        top_return = top_per_index.mean()
        bottom_return = bottom_per_index.mean()

        logger.info(f"Top {parameter:.2%} avg return: {top_return:.3%}")
        logger.info(f"Bottom {parameter:.2%} avg return: {bottom_return:.3%}")

        # hit_rate_positive_return = (target_pct_test.iloc[top_per_index] > 0).mean()
        # print(f"Hit rate for top {parameter:.2%} is {hit_rate_positive_return:.2%} ")

        # hit_rate_pnegative_return = (target_pct_test.iloc[top_per_index] < 0).mean()
        # print(f"Hit rate for bottom {parameter:.2%} is {hit_rate_pnegative_return:.2%} ")

        std_test = self._y_test.std()
        logger.info(f"y_test std: {std_test:.3%}")

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
        """
        Evaluate model performance using various metrics.

        Prints accuracy score, train/test accuracy, confusion matrix,
        classification report, ROC AUC score, and log loss.
        """
        accuracy = accuracy_score(self._y_test, self._y_pred)
        logger.debug(f"accuracy_score is : {accuracy}")
        train_acc = self._lgbm_model.score(
            self._X_train, self._y_train
        )  # accuracy on training data
        test_acc = self._lgbm_model.score(self._X_test, self._y_test)
        logger.debug(f"train_accuracy: {train_acc}")
        logger.debug(f"test_accuracy: {test_acc}")
        logger.debug(f"Confusion matrix:\n{confusion_matrix(self._y_test, self._y_pred)}")
        logger.debug(f"Classification report:\n{classification_report(self._y_test, self._y_pred)}")
        # auc = roc_auc_score(self._y_test, self._proba)
        auc = roc_auc_score(self._y_test, self._proba_test)
        logger.debug(f"roc_auc: {auc}")
        loss = log_loss(self._y_test, self._proba_test)
        logger.debug(f"log_Loss: {loss}")
        ml_flow__log_metrics("classification/accuracy_score", accuracy)
        ml_flow__log_metrics("classification/train_accuracy", train_acc)
        ml_flow__log_metrics("classification/test_accuracy", test_acc)
        ml_flow__log_metrics("classification/roc_auc", auc)
        ml_flow__log_metrics("classification/log_Loss", loss)

    def pipeline_with_time_series_split(self):
        """
        Execute pipeline using time series cross-validation.

        Splits data into 5 folds maintaining temporal order, trains separate models
        for each fold, and evaluates performance across time periods.
        """
        tscv = TimeSeriesSplit(n_splits=5)
        count = 0
        logger.debug("Start of the TimeSeriesSplit split : 5  ")
        report = Report_Summary()
        for train_idx, test_idx in tscv.split(self._x):
            with mlflow.start_run():
                # print(f'count print {count}')
                count = count + 1
                mlflow.log_param("fold", count)
                logger.debug(f"TimeSeriesSplit_split : {count}")
                # print(f'count print {count}')

                self._X_train, self._X_test = (
                    self._x.iloc[train_idx],
                    self._x.iloc[test_idx],
                )

                self._y_train, self._y_test = (
                    self._y.iloc[train_idx],
                    self._y.iloc[test_idx],
                )

                self.run_lgbm_classifier()
                self.backtest_strategy()
                self.evaluate_segments()
                self.shap_evaluation(count)
                self.different_params_setup()
                self.evaluating_backtest_strategy()
                report.report_pipeline(self.pre_data)
                logger.debug(f"storing report : {report.show_report()}")
                ml_flow__log_metrics("strategy/sharpe", self.pre_data["sharpe"])
                ml_flow__log_metrics("strategy/sharpe_trade", self.pre_data["sharpe_trade"])
                ml_flow__log_metrics("strategy/cagr_pct", self.pre_data["cagr"] * 100)

        logger.debug("End of the TimeSeriesSplit")

    def classification_model_pipeline(self, feat_dataframe):
        """
        Execute complete classification model pipeline.

        Orchestrates data preparation, train/test split, model training, backtesting,
        and feature importance analysis.

        Args:
            feat_dataframe (pd.DataFrame): Feature dataframe for modeling
        """
        # raw_dataframe = utils.clean_features(raw_dataframe)
        with mlflow.start_run():
            feat_dataframe = utils.clean_features(feat_dataframe)
            self.combine_dataframes(feat_dataframe)
            self.set_train_test_split()
            self.run_lgbm_classifier()
            self.save_model()
            self.backtest_strategy()
            # self.evaluate_segments()
            self.feature_importance()
            self.equity_curve_result()
            self.shap_evaluation()
            self.different_params_setup()
            self.evaluating_backtest_strategy()

            report = Report_Summary()
            report.report_pipeline(self.pre_data)
            logger.debug(f"self.pre_data : {self.pre_data}")
            logger.debug(f"sharpe: {self.pre_data['sharpe']}")
            logger.debug(report.show_report())
            ml_flow__log_metrics("strategy/sharpe", self.pre_data["sharpe"])
            ml_flow__log_metrics("strategy/sharpe_trade", self.pre_data["sharpe_trade"])
            ml_flow__log_metrics("strategy/cagr_pct", self.pre_data["cagr"] * 100)

    def classification_time_split_model_pipeline(self, feat_dataframe):
        """
        Execute classification pipeline with time series cross-validation.

        Args:
            feat_dataframe (pd.DataFrame): Feature dataframe for modeling
        """
        feat_dataframe = utils.clean_features(feat_dataframe)
        self.combine_dataframes(feat_dataframe)
        self.pipeline_with_time_series_split()

    def add_to_dict(self, key, value):
        self.pre_data[key] = value
        return self.pre_data

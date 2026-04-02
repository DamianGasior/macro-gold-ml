import pandas as pd
import numpy as np

# from feature_engineering import FeatureEngineering
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (
    accuracy_score,
    ConfusionMatrixDisplay,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    
)
from sklearn.model_selection import train_test_split
from sklearn.model_selection import TimeSeriesSplit
import logging
from pathlib import Path
from xgboost import XGBClassifier
import xgboost as xgb
import os
import matplotlib.pyplot as plt

current_dir = os.path.dirname(__file__)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class Classification_model:
    def __init__(self):
        self._combined_dataframe = pd.DataFrame()
        self._x = pd.DataFrame()
        self._y = pd.DataFrame()
        self._X_train = pd.DataFrame()
        self._X_test = pd.DataFrame()
        self._y_train = pd.DataFrame()
        self._y_test = pd.DataFrame()
        # self._pred: np.ndarray | None = None
        # self._model_random_forest: RandomForestClassifier | None = None

    @property
    def return_combined_dataframe(self) -> pd.DataFrame():
        return self._combined_dataframe

    def combine_dataframes(self, raw_data_df, feature_df):
        self._combined_dataframe = feature_df.join(
            raw_data_df[["USD_PLN"]], how="inner"
        )  # merging two df's  by dates, mathcing to dates in feature.df dataframe.
        # print(type(self._combined_dataframe))
        logging.debug(self._combined_dataframe.head(14))

        # line below; adding a new column, where we move the values from tomorrow to toda / from today to yesterday, and so on.
        # we compare of the value for tomorrow is  > or < than today
        # the result is, if true we assign 1 , if false we assign 0
        # sift(-1) becasue we want to predict the  quote for tomorrow, not for yesterday

        # self._combined_dataframe['target']=(self._combined_dataframe['USD_PLN'].shift(-1)>self._combined_dataframe['USD_PLN']).astype(int)
        self._combined_dataframe["target_5_return"] = (
            self._combined_dataframe["USD_PLN"].shift(-20)
            / self._combined_dataframe["USD_PLN"]
            - 1
        )
        self._combined_dataframe["target_5"] = (
            self._combined_dataframe["target_5_return"] > 0
        ).astype(int)

        # print(self._combined_dataframe.head(14))

        self._combined_dataframe = self._combined_dataframe.dropna()
        self._x = self._combined_dataframe.drop(
            columns=["target_5", "USD_PLN", "target_5_return"]
        )  # droppoing the selected columns, matrix with features

        self._y = self._combined_dataframe[
            "target_5"
        ]  # leaving selected columns df with target

        print(self._y.value_counts())

        # Below lines, counts how much in percentage there are results with '0' , how much with results '1'
        logging.info(
            f"\nClass balance/distribution/proportion of the target is: {self._y.value_counts(normalize=True)}"
        )

        # self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(
        #     self._x, self._y, test_size=0.2, shuffle=False
        # )

        # print(self._combined_dataframe.tail())

        return self._combined_dataframe
    
    def feature_importnace(self,model_input):

        importance=model_input.feature_importances_
        df_imp=pd.DataFrame({
            'feature' : self._X_train.columns ,
            'importance' : importance
        }).sort_values(by='importance', ascending=False)
        print(df_imp.head(25))
        cumsum = df_imp['importance'].cumsum()
        print(f"Cumsum results : \n {cumsum.head(25)}")

    def set_train_test_split(self):
        self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(
            self._x, self._y, test_size=0.2, shuffle=False
        )

    def run_random_forest_classifier(self):

        model = RandomForestClassifier(
            class_weight="balanced",
            max_depth=4,
            max_features="sqrt",
            min_samples_leaf=2,
            n_estimators=300,
            random_state=42,
        )
        print(
            f"""
        Model name is :  {type(model).__name__},
        model details are: {model.get_params()}"""
        )

        model.fit(self._X_train, self._y_train)
        proba = model.predict_proba(self._X_test)[
            :, 1
        ]  # pick up all the line, but only the second column, which is the one for class 1

        # numpy slicing
        # [:, :]  → wszcopy all  (without any changes)
        # [:, 1]  → one column  ( target score)
        # [1, :]  → one row

        prob_config = 0.45
        print(
            f"""
        proba.min:{proba.min()},
        proba.max: {proba.max()}
        Probability config is set to : {prob_config}
"""
        )

        pred = (proba > prob_config).astype(int)

        # print('model.predict_proba - self._X_test',model.predict_proba(self._X_test))
        # print(f"AUC : {roc_auc_score(self._y_test, sample)}")
        # print(f"check :{roc_auc_score(self._y_test, 1 - sample)}")

        return model, pred

    def histogram_result(self, name, model_input):
        plt.figure()  # opening clause
        proba_cal = model_input.predict_proba(self._X_test)[:, 1]
        plt.hist(proba_cal[self._y_test == 0], bins=25, alpha=0.5, label="class_0")
        plt.hist(proba_cal[self._y_test == 1], bins=25, alpha=0.5, label="class_1")
        plt.legend()
        plt.xlabel("predicted probability")
        plt.title("Proba distribution y class")
        plt.grid(True, linestyle="--", alpha=0.6)
        path_histogram = os.path.join(current_dir, f"{name}_histogram.jpg")
        plt.savefig(path_histogram)
        plt.close()  # clausing clause , helps to put all outputs into one fig

    def run_xgboost_model(self):
        model_xgbost = XGBClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=1,
            reg_lambda=1,
            random_state=42,
        )

        print(
            f"""
        Model name is :  {type(model_xgbost).__name__},
        model details are: {model_xgbost.get_params()}"""
        )

        print(self._X_train)
        print(self._y_train)
        model_xgbost.fit(self._X_train, self._y_train)
        label_predicted = model_xgbost.predict(self._X_test)

        return model_xgbost, label_predicted

    def evaluate_segments(self, model_input):

        top_threshold = 92
        bottom_threshold = 100 - top_threshold

        scores = model_input.predict_proba(self._X_test)[:, 1]

        top_percent = scores > np.percentile(scores, top_threshold)
        hit_top_rate = self._y_test[top_percent].mean()
        print(f"Hit top rate is  {bottom_threshold} %:", hit_top_rate)

        sum_top = np.sum(top_percent)
        print(f"Sum of top is {sum_top}\n")

        bottom_percent = scores < np.percentile(scores, bottom_threshold)
        hit_bottom_rate = self._y_test[bottom_percent].mean()
        print(f"Hit bottom rate is {bottom_threshold} %:", hit_bottom_rate)
        sum_bottom = np.sum(bottom_percent)
        print(f"bottom of top is {sum_bottom}\n")

        return None

    def confusion_matrix_graph(self, y_prediction, name: str):
        plt.figure()
        cm_result = ConfusionMatrixDisplay.from_predictions(
            self._y_test,
            y_prediction,
            display_labels=["USD_PLN", "USD_PLN"],
            cmap="Blues",
        )
        path_boost = os.path.join(current_dir, f"{name}_confusion_matrix.png")
        plt.savefig(path_boost)
        plt.close()
        return cm_result

    def different_params_setup(self, model_input, pred_input):
        accuracy = accuracy_score(self._y_test, pred_input)
        print(f"accuracy_score is : {accuracy}")
        train_acc = model_input.score(
            self._X_train, self._y_train
        )  # accuracy on training data
        test_acc = model_input.score(self._X_test, self._y_test)
        print(f"Train accuracy is : {train_acc}")
        print(f"Test accuracy is : {test_acc}")
        print(f"{confusion_matrix(self._y_test, pred_input)}")
        print(f"{classification_report(self._y_test, pred_input)}")

    def multiple_random_forest_combinations(self):
        param_grid = {
            "max_depth": [2, 3, 4],
            "min_samples_leaf": [ 3, 5,10],
            "n_estimators": [300],
            "max_features": ["sqrt"],
            "class_weight": ["balanced"],
            "random_state": [1],
            # "class_weight": [{0: 1, 1: 1.2}, {0: 1, 1: 1}],
        }
        rfst = RandomForestClassifier()
        grid = GridSearchCV(rfst, param_grid, cv=5, scoring="accuracy", n_jobs=-1)

        print(f"""model details are: {rfst}""")

        grid.fit(self._X_train, self._y_train)
        print(
            f"""grid.best_params_ : {grid.best_params_}
            grid.best_score_: {grid.best_score_}"""
        )

        best_model = grid.best_estimator_

        y_pred = best_model.predict(self._X_test)

        train_acc = best_model.score(
            self._X_train, self._y_train
        )  # accuracy on training data

        test_acc = best_model.score(self._X_test, self._y_test)  # accuracy on test data

        """
        if train_acc > test_acc , overfitting, model is to depth, model does remember the data, does not learn those
        if train_acc ,  test_acc both low, model does not learn 
        """

        print(f"Train accuracy is : {train_acc}")
        print(f"Test accuracy is : {test_acc}")

        print(classification_report(self._y_test, y_pred))

    def pipeline_with_time_series_split(self):
        tscv = TimeSeriesSplit(n_splits=5)

        regression_forest_in_splits = Classification_model()

        print("Start of the TimeSeriesSplit split : 5  ")

        for train_idx, test_idx in tscv.split(self._x):
            # print(train_idx)
            # print(test_idx)
            # print(self._x)

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

            model_random_forest, y_pred_rd_forest = self.run_random_forest_classifier()
            self.evaluate_segments(model_random_forest)
            self.different_params_setup(model_random_forest, y_pred_rd_forest)
            # regression_forest_in_splits.confusion_matrix_graph(y_pred_rd_forest,'random_forest')
            # regression_forest_in_splits.histogram_result('random_forest',model_random_forest)
        print("End of the TimeSeriesSplit")

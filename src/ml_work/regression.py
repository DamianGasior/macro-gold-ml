import pandas as pd
import numpy as np
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error,root_mean_squared_error

# from feature_engineering import FeatureEngineering
from sklearn.ensemble import RandomForestRegressor
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


class Regression_model:
    def __init__(self):
        self._combined_dataframe = pd.DataFrame()
        self._x = pd.DataFrame()
        self._y = pd.DataFrame()
        self._X_train = pd.DataFrame()
        self._X_test = pd.DataFrame()
        self._y_train = pd.DataFrame()
        self._y_test = pd.DataFrame()
        self._y_pred: np.ndarray | None = None
        self._model_forest_reg: RandomForestRegressor | None = None

    @property
    def return_combined_dataframe(self) -> pd.DataFrame():
        return self._combined_dataframe
    
    @property
    def return_X_train(self):
        return self._X_train 
    
    @property
    def return_model_f_reg(self):
        return self._model_forest_reg
    

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
        horizon = 5
        self._combined_dataframe["target"] = (
            self._combined_dataframe["USD_PLN"].shift(-horizon)
            / self._combined_dataframe["USD_PLN"]
            - 1
        )

        self._combined_dataframe = self._combined_dataframe.dropna()
        print(self._combined_dataframe.head(14))

        self._combined_dataframe = self._combined_dataframe.dropna()
        self._x = self._combined_dataframe.drop(
            columns=["target"]
        )  # droppoing the selected columns, matrix with features
        print(self._x)

        self._y = self._combined_dataframe[
            "target"
        ]  # leaving selected columns df with target
        # print(self._y)

        # Below lines, counts how much in percentage there are results with '0' , how much with results '1'
        logging.info(
            f"\nClass balance/distribution/proportion of the target is: {self._y.value_counts(normalize=True)}"
        )

        # self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(
        #     self._x, self._y, test_size=0.2, shuffle=False
        # )

        print(self._combined_dataframe.tail())

        return self._combined_dataframe

    def feature_importnace(self):

        importance = self._model_forest_reg.feature_importances_
        df_imp = pd.DataFrame(
            {"feature": self._X_train.columns, "importance": importance}
        ).sort_values(by="importance", ascending=False)
        print(df_imp.head(40))
        cumsum = df_imp["importance"].cumsum()
        print(f"Cumsum results : \n {cumsum.head(40)}")


    def set_train_test_split(self):
        self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(
            self._x, self._y, test_size=0.2, shuffle=False
        )

    def run_random_forest_regression(self):

        model = RandomForestRegressor(
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



        self._model_forest_reg = model.fit(self._X_train, self._y_train)
        y_pred = model.predict(self._X_test)
        self._y_pred = y_pred
        # print(self._y_pred)
 

        return y_pred

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

    def evaluate_segments(self):

        corr = np.corrcoef(self._y_pred, self._y_test)[0, 1]
        print(f'''\nCorrelation is {corr}
        
        In finance : 
        correlation	meaning
        0.05-0.15	weak signal
        0.2-0.3	OK
        0.3-0.5	strong singanl ✅
        >0.5	rare / suspiciously high
        ''')
        
        parameter=0.05
        len_of_data=len(self._y_pred)
        k=int(parameter * len_of_data)

        assert len(self._y_pred) == len(self._y_test), 'y_test and y_pred do not have the same lenght'

        # print(k)
        y_pred_sorted=np.argsort(self._y_pred)
        # print(y_pred_sorted)

        top_per_index = y_pred_sorted[-k:]
        bottom_per_index = y_pred_sorted[:k]

        top_return = self._y_test.iloc[top_per_index].mean()
        bottom_return = self._y_test.iloc[bottom_per_index].mean()

        print(f"Top {parameter:.2%}  avg return: {top_return}, in  pct it is :{top_return:.3%}")
        print(f"Bottom {parameter:.2%}  avg return:{bottom_return}, in  pct it is :{bottom_return:.3%}")
        
        hit_rate_positive_return=(self._y_test.iloc[top_per_index]>0).mean()
        print(f'Hit rate for top {parameter:.2%} is {hit_rate_positive_return:.2%} ')

        hit_rate_pnegative_return=(self._y_test.iloc[top_per_index]<0).mean()
        print(f'Hit rate for bottom {parameter:.2%} is {hit_rate_pnegative_return:.2%} ')


        std_test=self._y_test.std()
        print(f"\ny_test std: {std_test},in  pct it is :{std_test:.3%}\n")

        mae=round(mean_absolute_error(self._y_test, self._y_pred),6)
        mse=mean_squared_error(self._y_test, self._y_pred)
        rmse=root_mean_squared_error(self._y_test, self._y_pred)
        r2=r2_score(self._y_test, self._y_pred)
        
        print(f"MAE test: {mae}, in  pct it is :{mae:.3%}; average model mistake vs std: {std_test:.3%}")  # its not sensitive on outliers, hence the punishment on errors is not so big
        print(f"MSE test: {mse},in  pct it is :{mse:.3%}") # big errors are punished heavily , moslty used when big errors can be costly in the decision 
        print(f"RMSE: ,{rmse},in  pct it is :{rmse:.3%}; how model does punish bigger mistakes, compare against  std: {std_test:.3%}") # how the model makes bad predictions /errors, where big mistakes are punished more
        print(f"R2 test: {r2},in  pct it is :{r2:.3%}") # not so useful here, it tells how much of it , comes form the model
        

        RMSE_std=rmse/std_test

        print(f'''RMSE_std is equal to : {RMSE_std}'
                result	meaning
        < 0.5	very good model
        ~1.0	model ≈ noise
        > 1.0	model weak''')

        # directional accuracy, does the model recognize/predict the direction ( up or down)
        # 50 % is random, going above that is fine
        direction_true = np.sign(self._y_test)
        direction_pred = np.sign(self._y_pred)
        da=np.mean(direction_true==direction_pred)
        print(f"\nDirection accuracy is:, {da:.3%}, which tells us if we hit correctly te direction(sign);\nremeber : 50 % is random, above that its an edge" )
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
            "max_depth": [2, 3, 4,5],
            "min_samples_leaf": [3, 5, 10],
            "n_estimators": [300,400,500],
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

        train_r2=best_model.score(self._X_train, self._y_train)
        test_r2=best_model.score(self._X_test, self._y_test)

        print(f"Train R2: {train_r2}")
        print(f"Test R2 : {test_r2}")

        

    def pipeline_with_time_series_split(self):
        tscv = TimeSeriesSplit(n_splits=5)
        count=0
        print("Start of the TimeSeriesSplit split : 5  ")

        for train_idx, test_idx in tscv.split(self._x):
            # print(f'count print {count}')
            count=count+1
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
        self.combine_dataframes(raw_dataframe, feat_dataframe)
        self.set_train_test_split()
        self.run_random_forest_regression()
        self.evaluate_segments()
        self.feature_importnace()
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





    

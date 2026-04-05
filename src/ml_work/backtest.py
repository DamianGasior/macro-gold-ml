from src.ml_work.regression import Regression_model
from src.ml_work.trading_estimates import Trading_venue
import numpy as np
import pandas as pd




class Backtest:
    def __init__(self):
        self.train_pred : np.ndarray | None = None
        self.threshold_top : np.float64 | None = None
        self.threshold_bottom : np.float64 | None = None
        self.backtest_df : pd.DataFrame | None = None


# do y_trained data, zaczac dodawac nowe ceny

# assert predicted_data==self.train_pred , 'data are not the  same '


# backtest_trading=Trading_venue()

# predicted_values,threshold_top,threshold_bottom=backtest_trading.predict_and_threshold(trained_data=,model=)




def backtest_trade(self,test_data,model):
    test_data




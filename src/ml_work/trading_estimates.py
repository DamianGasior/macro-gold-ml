# nowa klasa , gdzie tu bede uderzal o parametry ustalone w refresssion.py, tam pewnie bede musial ustawic jakis 
# @proerpty files
import pandas as pd
import numpy as np
from src.ml_work.regression import Regression_model


class Trading_venue:
    def __init__(self):
        self.train_pred : np.ndarray | None = None
        self.threshold_top : np.float64 | None = None
        self.threshold_bottom : np.float64 | None = None
        




    def predict_and_threshold(self,train,model):

        self.train_pred = model.predict(train) # usinf the already trained models isntance
        self.threshold_top=np.percentile(train , 95)
        self.threshold_bottom=np.percentile(train,5)

    # def buy_sell_signal(self,train,model,):
    #     if self._y_pred[0] > threshold_top:
    #         print('Buy the underlying asset')
    #     elif self._y_pred[0] < threshold_bottom:
    #         print('Short/sell the underlying asset')
    #     else:
    #         print('There is no trading opportunity')




    # def trading_pipeline(self):
    #     self.buy_sell_signal()
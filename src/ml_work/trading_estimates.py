# nowa klasa , gdzie tu bede uderzal o parametry ustalone w refresssion.py, tam pewnie bede musial ustawic jakis 
# @proerpty files
import numpy as np


class Trading_venue:
    def __init__(self):
        self.train_pred : np.ndarray | None = None
        self.threshold_top : np.float64 | None = None
        self.threshold_bottom : np.float64 | None = None
        




    def predict_and_threshold(self,trained_data,model):

        self.train_pred = model.predict(trained_data) # usinf the already trained models isntance
        print(f'Min data : {self.train_pred.min()}, Max data : {self.train_pred.max()}')
        self.threshold_top=np.percentile(self.train_pred , 95)
        self.threshold_bottom=np.percentile(self.train_pred,5)

    def buy_sell_signal(self,latest_data,model):
   
        new_data=latest_data.iloc[-1:]  # [-1:] helps to return a dataframe
        
        y_pred=model.predict(new_data)
        pred=y_pred[0]

        print(f'predicted value is : {pred}')
        print(f'predicted threshold top is : {self.threshold_top}')
        print(f'predicted threshold bottom is : {self.threshold_bottom}')
        print(f"Percentile pred_today: {(pred > self.train_pred).mean():.3%}")



        if pred > self.threshold_top:
            print('Buy the underlying asset')
        elif pred < self.threshold_bottom:
            print('Short/sell the underlying asset')
        else:
            print('There is no trading opportunity')




    def trading_pipeline(self,trained_data,model,latest_data):
        # self.predict_and_threshold(trained_data,model)

        self.predict_and_threshold(trained_data,model)
        self.buy_sell_signal(latest_data,model)
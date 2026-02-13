import pandas as pd
# from feature_engineering import FeatureEngineering
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import logging


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)



class Classification_model:
    def __init__(self):
        self._combined_dataframe=pd.DataFrame()
        self._x=pd.DataFrame()
        self._y=pd.DataFrame()
        self._x_train=pd.DataFrame()
        self._x_test=pd.DataFrame()
        self._y_train=pd.DataFrame()
        self._y_test=pd.DataFrame()



    @property
    def return_combined_dataframe(self) -> pd.DataFrame():
        return self._combined_dataframe
    

    def combine_dataframes(self,raw_data_df,feature_df):
        split = int(len(df) * 0.8)        
        # print(feature_df.tail(14))
        # print(feature_df.head(14))
        self._combined_dataframe=feature_df.join(raw_data_df[['USD_PLN']],how='inner')
        # print(type(self._combined_dataframe))
        print(self._combined_dataframe.head(14))
        
        print(self._combined_dataframe.head(14)) 
        self._combined_dataframe['target']=(self._combined_dataframe['USD_PLN'].shift(-1)>self._combined_dataframe['USD_PLN']).astype(int)
        print(self._combined_dataframe.head(14))
        self._combined_dataframe=self._combined_dataframe.dropna() 
        self._x=self._combined_dataframe.drop(columns=['target','USD_PLN'])
        print(self._x.head(14))
        self._y=self._combined_dataframe['target']
        print(self._y.head(14))
        split = int(len(self._y) * 0.8)

        
        logging.info(f'Class balance of the target is: {self._y.value_counts(normalize=True)}')
        
        self._x_train=self._x.iloc[:split]
        self._x_test=self._x.iloc[split:]
        self._y_train=self._y.iloc[:split]
        self._y_test=self._y.iloc[split:]
        
        return self._combined_dataframe 

        





import pandas as pd
import numpy as np
# from feature_engineering import FeatureEngineering
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_auc_score
import logging


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)



class Classification_model:
    def __init__(self):
        self._combined_dataframe=pd.DataFrame()
        self._x=pd.DataFrame()
        self._y=pd.DataFrame()
        self._X_train=pd.DataFrame()
        self._X_test=pd.DataFrame()
        self._y_train=pd.DataFrame()
        self._y_test=pd.DataFrame()



    @property
    def return_combined_dataframe(self) -> pd.DataFrame():
        return self._combined_dataframe
    

    def combine_dataframes(self,raw_data_df,feature_df):
        # split = int(len(feature_df) * 0.8)        
        # print(feature_df.tail(14))
        # print(feature_df.head(14))
        self._combined_dataframe=feature_df.join(raw_data_df[['USD_PLN']],how='inner') # merging two df's  by dates, mathcing to dates in feature.df dataframe.
        # print(type(self._combined_dataframe))
        print(self._combined_dataframe.head(14))
        
        print(self._combined_dataframe.head(14)) 
        # line below; adding a new column, where we move the values from tomorrow to toda / from today to yesterday, and so on.  
        # we compare of the value for tomorrow is  > or < than today
        # the result is, if true we assign 1 , if false we assign 0
        # sift(-1) becasue we want to predict the  quote for tomorrow, not for yesterday

        # self._combined_dataframe['target']=(self._combined_dataframe['USD_PLN'].shift(-1)>self._combined_dataframe['USD_PLN']).astype(int) 
        self._combined_dataframe['target_5_return']=self._combined_dataframe['USD_PLN'].shift(-5)/self._combined_dataframe['USD_PLN']-1
        self._combined_dataframe['target_5']=(self._combined_dataframe['target_5_return']>0).astype(int) 

        
      
        print(self._combined_dataframe.head(14))

        self._combined_dataframe=self._combined_dataframe.dropna() 
        self._x=self._combined_dataframe.drop(columns=['target_5','USD_PLN','target_5_return']) # droppoing the selected columns, matrix with features 

        self._y=self._combined_dataframe['target_5']  # leaving selected columns df with target 

        split = int(len(self._y) * 0.8)

        # Below lines, counts how much in percentage there are results with '0' , how much with results '1'
        logging.info(f'Class balance/distribution/proportion of the target is: {self._y.value_counts(normalize=True)}')
        
        self._X_train=self._x.iloc[:split]
        self._X_test=self._x.iloc[split:]
        self._y_train=self._y.iloc[:split]
        self._y_test=self._y.iloc[split:]

        
        return self._combined_dataframe 



    def run_random_forest_classifier(self):
        model = RandomForestClassifier(n_estimators=300, max_depth=5, random_state=42)
        model.fit(self._X_train, self._y_train)
        pred = model.predict(self._X_test)
        print(f'accuracy_score is : {accuracy_score(self._y_test, pred)}')
        print(f'length is : {len(self._y_test)}')
        print(f'{confusion_matrix(self._y_test, pred)}')
        print(f'{classification_report(self._y_test, pred)}')
        sample = model.predict_proba(self._X_test)[:, 1]
        # print(f'sample print: {sample}')
        print(type(sample))

        # threshhold=np.quantile(sample,0.80)
        # mask=sample >= threshhold

        threshhold=np.quantile(sample,0.20)
        mask=sample <= threshhold

        # print('model.predict_proba - self._X_test',model.predict_proba(self._X_test))
        print(f'AUC : {roc_auc_score(self._y_test, sample)}')
        print(f'check :{roc_auc_score(self._y_test, 1 - sample)}')

        accuracy_top20=accuracy_score(self._y_test[mask],(sample[mask] > 0.5).astype(int))

        # print("Liczba obserwacji w top 20%:", mask.sum())
        # print("Accuracy dla top 20%:", accuracy_top20)

        
        print("Liczba obserwacji w bottom 20%:", mask.sum())
        print("Accuracy dla bottom 20%:", accuracy_top20)

       
        return_test=self._combined_dataframe.loc[self._X_test.index,'target_5_return']
        mean_return_bottom20=return_test[mask].mean()
        print("Średni 5-day return dla bottom 20%:", mean_return_bottom20)



        return accuracy_score


#  https://chatgpt.com/g/g-p-6966ca2b44888191852c15e94adfa88b-pierwszeaiprojekty/c/698b7ff9-87fc-8325-bda8-9ecfae91dc26






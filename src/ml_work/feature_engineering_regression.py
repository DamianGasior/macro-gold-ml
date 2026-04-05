# from src.pipeline.pipeline import DataPipeline
import itertools

import numpy as np
import pandas as pd


class FeatureRegressionEngineering:
    def __init__(self):
        self._dataframe = pd.DataFrame()

    @property
    def return_dataframe(self) -> pd.DataFrame:
        return self._dataframe


    def correlation_betwee_instrumentss(self, *args):
        for arg1, arg2 in itertools.combinations(args, 2):
            self._dataframe[f"corr_{arg1}_{arg2}"] = ((self._dataframe[f"{arg1}_change"]).rolling(5).corr(self._dataframe[f"{arg2}_change"]))

        print(self._dataframe.tail(10))
        return self._dataframe

    # def yield_spread_next_features(self,yield1, yield2)
    #     # _spread
    #     cols=self._dataframe[self._dataframe.columns.str.contains(f"{yield1}_{yield2}_spread",case=False)]
    #     self._dataframe[f"{yield1}_{yield2}_spread_lag_1"]=self._dataframe[cols].shift(1)
    #     print(self._dataframe.tail())
    #     print(type(self._dataframe))

    def clean_features(self):
        # zamień inf/-inf na NaN
        self._dataframe.replace([np.inf, -np.inf], np.nan, inplace=True)
        # wypełnij NaN zerem (lub inną logiką np. średnią kolumny)
        self._dataframe.fillna(0, inplace=True)
        return self._dataframe


    def feature_enginerring_pipeline(self,dataframe):
        # print(dataframe.head(10))
        self.basic_metrics(dataframe)
        self.z_score(dataframe)
        # self.ratios(dataframe,'GLD','UUP','USD_PLN')
        self.ratios2(dataframe,'GOLD')
        self.clean_features()
        self.spread_between_yields(dataframe,'US10Y','US5Y')
        # self.correlation_between_instruments(dataframe)
        return self._dataframe
    
    def z_score(self,dataframe):
        '''
        this method will help to assess how far the values are from the average, results will be normalized, so accross all assets classess the model can read it easily
        '''
        dataframe = (dataframe.sort_index())  #sorting from the oldest on the top to the newest on the bottom, most of the fuction in pandas expect that the previous row is the earlierst one
        columns=list(dataframe.columns) 
        
        new_zscore_results={}

        for symbol in columns:
            series=dataframe[symbol].shift(1)
            roll_mean = series.rolling(20).mean()
            roll_std = series.rolling(20).std()
            print(roll_mean)
            print(roll_std)
            print(series)

            new_zscore_results[f"{symbol}_zscore_20"] = (series - roll_mean) / roll_std
        self._dataframe=pd.concat([self._dataframe,pd.DataFrame(new_zscore_results)],axis=1)  
        print(self._dataframe.tail(20))
        return self._dataframe





    def basic_metrics(self, dataframe):
        dataframe = (dataframe.sort_index())  #sorting from the oldest on the top to the newest on the bottom, most of the fuction in pandas expect that the previous row is the earlierst one
        columns=list(dataframe.columns)  
        print(columns)
        for symbol in columns:
            
            if 'CPI' in symbol:
                price_lag=dataframe[symbol].shift(2)
            else:
                price_lag=dataframe[symbol].shift(1)

            self._dataframe[f"{symbol}_return_1"] = price_lag.pct_change(1)
            self._dataframe[f"{symbol}_return_2"] = price_lag.pct_change(2)
            self._dataframe[f"{symbol}_return_3"] = price_lag.pct_change(3)
            # self._dataframe[f"{symbol}_return_4"] = price_lag.pct_change(4)
            self._dataframe[f"{symbol}_return_5"] = price_lag.pct_change(5)
            self._dataframe[f"{symbol}_return_10"] = price_lag.pct_change(10)
            self._dataframe[f"{symbol}_return_20"] = price_lag.pct_change(20)
            self._dataframe[f"{symbol}_return_30"] = price_lag.pct_change(30)
            self._dataframe[f"{symbol}_return_50"] = price_lag.pct_change(30)


            self._dataframe[f"{symbol}_momentum_ratio"] = self._dataframe[f"{symbol}_return_10"] / self._dataframe[f"{symbol}_return_20"] 

            self._dataframe[f"{symbol}_rolling_mean_5"] = self._dataframe[f"{symbol}_return_1"].rolling(5).mean()
            self._dataframe[f"{symbol}_rolling_mean_10"] = self._dataframe[f"{symbol}_return_1"].rolling(10).mean()
            self._dataframe[f"{symbol}_rolling_mean_20"] = self._dataframe[f"{symbol}_return_1"].rolling(20).mean()


            self._dataframe[f"{symbol}_vol_10"] = self._dataframe[f"{symbol}_return_1"].rolling(5).std()
            self._dataframe[f"{symbol}_vol_30"] = self._dataframe[f"{symbol}_return_1"].rolling(30).std()
            self._dataframe[f"{symbol}_vola_ratio_10/30"] = self._dataframe[f"{symbol}_vol_10"] / self._dataframe[f"{symbol}_vol_30"]
            self._dataframe[f"{symbol}_high_vol"] = self._dataframe[f"{symbol}_vol_30"] / self._dataframe[f"{symbol}_vol_30"].rolling(50).mean()

            rolling_max=price_lag.rolling(20).max()
            rolling_min=price_lag.rolling(20).min()
            
           
            self._dataframe[f"{symbol}_range_position"]=(price_lag - rolling_min)/(rolling_max-rolling_min) # tells us where we are  between the min and low
            '''
            ~0 → oversold / low
            ~1 → overbought / high
            ~0.5 → neutral
            '''

        print(self._dataframe.tail(20))
        return self._dataframe
    

    def ratios(self, dataframe,gold,dxy,usd_pln):
        self._dataframe[f"{usd_pln}_{dxy}_return_diff"] = dataframe[usd_pln].shift(1).pct_change() - dataframe[dxy].shift(1).pct_change() 
        self._dataframe[f"{usd_pln}_{gold}_return_diff"] = dataframe[usd_pln].shift(1).pct_change() - dataframe[gold].shift(1).pct_change() 
        return self._dataframe
    
    def ratios2(self, dataframe,underlying):
        for col in dataframe.columns:
            if col!=underlying:
                self._dataframe[f"{underlying}_{col}_return_diff"] = dataframe[underlying].shift(1).pct_change() - dataframe[col].shift(1).pct_change() 
        return self._dataframe


# to be removed , I will be taking the spreads from fred directly 
    def spread_between_yields(self,dataframe,US_yield_one,US_yield_two):
        us_price_lag_1=dataframe[US_yield_one].shift(1)
        us_price_lag_2=dataframe[US_yield_two].shift(1)
        self._dataframe[f"{US_yield_one}_{US_yield_two}_spread"] = us_price_lag_1 - us_price_lag_2
        return self._dataframe




    

    # def correlation_between_instruments(self,dataframe):
    #     columns=list(dataframe.columns)  
    #     for symbol1, symbol2 in itertools.combinations(columns, 2):
    #         self._dataframe[f"corr_{symbol1}_{symbol2}"] = ((self._dataframe[f"{symbol1}_change"]).rolling(20).corr(self._dataframe[f"{symbol2}_change"]))

    #     print(self._dataframe.tail(10))
    #     return self._dataframe
   
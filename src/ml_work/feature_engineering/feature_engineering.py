# from src.pipeline.pipeline import DataPipeline
import pandas as pd
import itertools

# #  USD/PLN  EUR/USD  DGS10  10yply.b


# df = DataPipeline.merged_dataframe
# print(df)


class FeatureEngineering:
    def __init__(self):
        self._dataframe = pd.DataFrame()

    @property
    def fe_dataframe(self) -> pd.DataFrame:
        return self._dataframe

    def currency_features(self, dataframe, *args):
        print(type(dataframe))
        dataframe = (dataframe.sort_index())  # sorting from the oldest on the top to the newest on the bottom, most of the fuction in pandas expect that the previous row is the earlierst one
        for ccy_pair in args:
            self._dataframe[f"{ccy_pair}_lag_1"] = dataframe[ccy_pair].shift(1)  # creating one column and moving it down by 1
            self._dataframe[f"{ccy_pair}_roll_5"] = (self._dataframe[f"{ccy_pair}_lag_1"].rolling(5).mean())
            self._dataframe[f"{ccy_pair}_momentum_5"] = (self._dataframe[f"{ccy_pair}_lag_1"].rolling(5).mean().diff())  # taking the values from lag_1 , caclulcation the rolling mean and then the difference between those
            self._dataframe[f"{ccy_pair}_std_5"] = (self._dataframe[f"{ccy_pair}_lag_1"].rolling(5).std())
            self._dataframe[f"{ccy_pair}_roll_10"] = (self._dataframe[f"{ccy_pair}_lag_1"].rolling(10).mean())
            self._dataframe[f"{ccy_pair}_momentum_10"] = (self._dataframe[f"{ccy_pair}_lag_1"].rolling(10).mean().diff())
            self._dataframe[f"{ccy_pair}_std_10"] = (self._dataframe[f"{ccy_pair}_lag_1"].rolling(10).std())
            self._dataframe[f"{ccy_pair}_change"] = self._dataframe[f"{ccy_pair}_lag_1"].pct_change()
            # print(self._dataframe.head())

    



            # self.dataframe=self.dataframe.dropna()
            # print(self._dataframe)
            # print(self._dataframe.head())
            # print(self._dataframe.tail(15))
            print(type(self._dataframe))

        return self._dataframe

    def yield_spread_features(self, dataframe, yield1, yield2):
        self._dataframe[f"{yield1}_{yield2}_spread"] = (dataframe[yield1] - dataframe[yield2])
        self._dataframe[f"{yield1}_{yield2}_spread_lag_1"] = self._dataframe[f"{yield1}_{yield2}_spread"].shift(1)
        self._dataframe[f"{yield1}_{yield2}_spread_roll_5"] = (self._dataframe[f"{yield1}_{yield2}_spread_lag_1"].rolling(5).mean())
        self._dataframe[f"{yield1}_{yield2}_spread_momentum_5"] = (self._dataframe[f"{yield1}_{yield2}_spread_lag_1"].rolling(5).mean().diff())
        self._dataframe[f"{yield1}_{yield2}_spread_std_5"] = (self._dataframe[f"{yield1}_{yield2}_spread_lag_1"].rolling(5).std())
        self._dataframe[f"{yield1}_{yield2}_spread_roll_10"] = (self._dataframe[f"{yield1}_{yield2}_spread_lag_1"].rolling(10).mean())
        self._dataframe[f"{yield1}_{yield2}_spread_momentum_10"] = (self._dataframe[f"{yield1}_{yield2}_spread_lag_1"].rolling(10).mean().diff())
        self._dataframe[f"{yield1}_{yield2}_spread_std_10"] = (self._dataframe[f"{yield1}_{yield2}_spread_lag_1"].rolling(10).std())
        # self._dataframe[f"{yield1}_lag_1"] = dataframe[yield1].shift(1)
        # self._dataframe[f"{yield1}_change"] = self._dataframe[f"{yield1}_lag_1"].pct_change()
        # self._dataframe[f"{yield2}_lag_1"] = dataframe[yield2].shift(1)
        # self._dataframe[f"{yield2}_change"] = self._dataframe[f"{yield2}_lag_1"].pct_change()
        return self._dataframe

    def etf_features(self, dataframe, *args):
        for etf in args:
            self._dataframe[f"{etf}_lag_1"] = dataframe[etf].shift(1)
            self._dataframe[f"{etf}_change"] = self._dataframe[f"{etf}_lag_1"].pct_change()
            self._dataframe[f"{etf}_roll_5"] = (self._dataframe[f"{etf}_change"].rolling(5).mean())
            self._dataframe[f"{etf}_vol"] = self._dataframe[f"{etf}_roll_5"].std()
            print(type(self._dataframe))
            print(self._dataframe.head())

        return self._dataframe

    # def etf_ccy_features(self, ccy_pair, *args):

    #     for etf in args:
    #         self._dataframe[f"{etf}_{ccy_pair}_corr"] = self._dataframe[f"{etf}_roll_5"].corr(self._dataframe[f"{ccy_pair}_change"])
    #         print(self._dataframe.tail(10))

    #     return self._dataframe

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


    def feature_enginerring_pipeline(self,dataframe):
        self.basic_metrics(dataframe)
        self.z_score(dataframe)
        self.ratios(dataframe,'GLD','UUP','US10Y','EUR_USD','USD_PLN','PL10Y')
        # self.correlation_between_instruments(dataframe)


        return self._dataframe
    
    def z_score(self,dataframe):
        '''
        this method will help to assess how far the values are from the average, results will be normalized, so accross all assets classess the model can read it easily
        '''
        dataframe = (dataframe.sort_index())  #sorting from the oldest on the top to the newest on the bottom, most of the fuction in pandas expect that the previous row is the earlierst one
        columns=list(dataframe.columns)  
        print(columns)
        for symbol in columns:
            series=dataframe[symbol].shift(1)
            roll_mean = series.rolling(10).mean()
            roll_std = series.rolling(10).std()
            print(roll_mean)
            print(roll_std)
            print(series)

            self._dataframe[f"{symbol}_zscore"] = (series - roll_mean) / roll_std
        print(self._dataframe.tail(20))
        return self._dataframe





    def basic_metrics(self, dataframe):
        dataframe = (dataframe.sort_index())  #sorting from the oldest on the top to the newest on the bottom, most of the fuction in pandas expect that the previous row is the earlierst one
        columns=list(dataframe.columns)  
        print(columns)
        for symbol in columns:
            returns=dataframe[symbol].pct_change()
            returns_lag=returns.shift(1)
            self._dataframe[f"{symbol}_mom_5"] = (dataframe[symbol].shift(1) - dataframe[symbol].shift(6))/dataframe[symbol].shift(6)
            # self._dataframe[f"{symbol}_mom_10"] = (dataframe[symbol].shift(1) - dataframe[symbol].shift(11))/dataframe[symbol].shift(11)
            # self._dataframe[f"{symbol}_mom_roll_mean_5"] = dataframe[symbol].shift(1).rolling(5).mean().diff()
            # self._dataframe[f"{symbol}_mom_roll_mean_10"] = dataframe[symbol].shift(1).rolling(5).mean().diff()
            # self._dataframe[f"{symbol}_vol_5"]=returns_lag.rolling(5).std() # firstly you calculate the returns, then you move by 1 down ( to avoid data leakage) and then you cacl roll(5) and std
            # self._dataframe[f"{symbol}_vol_10"]=returns_lag.rolling(10).std()
            self._dataframe[f"{symbol}_vol_ratio"]=returns_lag.rolling(5).std()/returns_lag.rolling(20).std() # volatility ratio, if short term vol will rise against the longer one, it will tell that somehting start to happen 
            self._dataframe[f"{symbol}_vol_regime"] = (returns_lag.rolling(5).std() > returns_lag.rolling(20).std()).astype(int)

            self._dataframe[f"{symbol}_change"] = returns_lag
            self._dataframe[f"{symbol}_roll_5"] = dataframe[symbol].shift(1).rolling(20).mean()
            

        print(self._dataframe.tail(20))
        return self._dataframe
    

    def ratios(self, dataframe,gold,dxy,us_yield,usd_eur,usd_pln,pl_yields):

        self._dataframe[f"{gold}_{dxy}_ratio"] = dataframe[gold].shift(1) / dataframe[dxy].shift(1)
        self._dataframe[f"{usd_eur}_vs_{us_yield}"] = dataframe[usd_eur].shift(1) / dataframe[us_yield].shift(1)
        self._dataframe[f"{usd_pln}_vs_{pl_yields}"] = dataframe[usd_pln].shift(1) / dataframe[pl_yields].shift(1)

        return self._dataframe
    

    # def correlation_between_instruments(self,dataframe):
    #     columns=list(dataframe.columns)  
    #     for symbol1, symbol2 in itertools.combinations(columns, 2):
    #         self._dataframe[f"corr_{symbol1}_{symbol2}"] = ((self._dataframe[f"{symbol1}_change"]).rolling(5).corr(self._dataframe[f"{symbol2}_change"]))

    #     print(self._dataframe.tail(10))
    #     return self._dataframe
    '''
    does not help a lot : 
    
                     feature  importance
14            UUP_roll_5    0.081092
9         EUR_USD_roll_5    0.066952
24           EPOL_roll_5    0.056023
29            SPY_roll_5    0.055453
34          US10Y_roll_5    0.053413
4         USD_PLN_roll_5    0.052581
39          PL10Y_roll_5    0.051574
50      USD_PLN_vs_PL10Y    0.043563
49      EUR_USD_vs_US10Y    0.032638
65         corr_UUP_EPOL    0.028370
31       US10Y_vol_ratio    0.026803
68        corr_UUP_PL10Y    0.020867
30          US10Y_mom_10    0.016881
59      corr_EUR_USD_GLD    0.016435
78      corr_US10Y_PL10Y    0.015729
48         GLD_UUP_ratio    0.015398
58      corr_EUR_USD_UUP    0.015258
0         USD_PLN_mom_10    0.015216
16         GLD_vol_ratio    0.014747
8         EUR_USD_change    0.013615
5         EUR_USD_mom_10    0.013137
54     corr_USD_PLN_EPOL    0.012862
44           EPOL_zscore    0.012251
62    corr_EUR_USD_US10Y    0.012018
51  corr_USD_PLN_EUR_USD    0.011299
'''

        




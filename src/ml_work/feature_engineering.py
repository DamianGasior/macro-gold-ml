# from src.pipeline.pipeline import DataPipeline
import pandas as pd

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
        dataframe=dataframe.sort_index() # sorting from the oldest on the top to the newest on the bottom, most of the fuction in pandas expect that the previous row is the earlierst one
        for ccy_pair in args:
            self._dataframe[f"{ccy_pair}_lag_1"] = dataframe[ccy_pair].shift(1)
            self._dataframe[f"{ccy_pair}_roll_5"] = self._dataframe[f"{ccy_pair}_lag_1"].rolling(5).mean()
            self._dataframe[f"{ccy_pair}_momentum_5"] = self._dataframe[f"{ccy_pair}_lag_1"].rolling(5).mean().diff()
            self._dataframe[f"{ccy_pair}_std_5"] = self._dataframe[f"{ccy_pair}_lag_1"].rolling(5).std()
            self._dataframe[f"{ccy_pair}_roll_10"] = self._dataframe[f"{ccy_pair}_lag_1"].rolling(10).mean()
            self._dataframe[f"{ccy_pair}_momentum_10"] = self._dataframe[f"{ccy_pair}_lag_1"].rolling(10).mean().diff()
            self._dataframe[f"{ccy_pair}_std_10"] = self._dataframe[f"{ccy_pair}_lag_1"].rolling(10).std()
            self._dataframe[f"{ccy_pair}_change"] = self._dataframe[f"{ccy_pair}_lag_1"].pct_change()
            print(self._dataframe.head())

            # self.dataframe=self.dataframe.dropna()
            # print(self._dataframe)
            # print(self._dataframe.head())
            print(self._dataframe.tail())
            print(type(self._dataframe))

        return self._dataframe

    def yield_spread_features(self, dataframe, yield1, yield2):
        self._dataframe[f"{yield1}_{yield2}_spread"] = (dataframe[yield1] - dataframe[yield2])
        self._dataframe[f"{yield1}_{yield2}_spread_lag_1"] = self._dataframe[f"{yield1}_{yield2}_spread"].shift(1)
        self._dataframe[f"{yield1}_{yield2}_spread_roll_5"] = self._dataframe[f"{yield1}_{yield2}_spread_lag_1"].rolling(5).mean()
        self._dataframe[f"{yield1}_{yield2}_spread_momentum_5"] = self._dataframe[f"{yield1}_{yield2}_spread_lag_1"].rolling(5).mean().diff()
        self._dataframe[f"{yield1}_{yield2}_spread_std_5"] = self._dataframe[f"{yield1}_{yield2}_spread_lag_1"].rolling(5).std()
        self._dataframe[f"{yield1}_{yield2}_spread_roll_10"] = self._dataframe[f"{yield1}_{yield2}_spread_lag_1"].rolling(10).mean()
        self._dataframe[f"{yield1}_{yield2}_spread_momentum_10"] = self._dataframe[f"{yield1}_{yield2}_spread_lag_1"].rolling(10).mean().diff()
        self._dataframe[f"{yield1}_{yield2}_spread_std_10"] = self._dataframe[f"{yield1}_{yield2}_spread_lag_1"].rolling(10).std()
        return self._dataframe
    
    # def yield_spread_next_features(self,yield1, yield2)
    #     # _spread
    #     cols=self._dataframe[self._dataframe.columns.str.contains(f"{yield1}_{yield2}_spread",case=False)]
    #     self._dataframe[f"{yield1}_{yield2}_spread_lag_1"]=self._dataframe[cols].shift(1)
    #     print(self._dataframe.tail())
    #     print(type(self._dataframe))


# from src.pipeline.pipeline import DataPipeline
import itertools
from itertools import product


import numpy as np
import pandas as pd

from src.pipeline.utils import (
    SYMBOL_MAPPINGS,
    OTHER,
    BASE_UNDERLYING,
    VIX_SYMBOLS,
    CCY_SYMBOLS,
    RATES,
    REAL_YIELDS,
    ETF,COMM,
    RATE_DIFF,
    INFL_EXP,
    CPI,
    CRYPTOS,
    DXY,
)


class FeatureRegressionEngineering:
    def __init__(self):
        self._df = pd.DataFrame()

    @property
    def return_dataframe(self) -> pd.DataFrame:
        return self._df

    def feature_enginerring_pipeline(self, dataframe):
        self.dxy_builder(dataframe)
        self.basic_metrics(dataframe, VIX_SYMBOLS, ETF,COMM, DXY,BASE_UNDERLYING)
        self.z_score(20, ETF, COMM,DXY,BASE_UNDERLYING)
        self.ratios(1, BASE_UNDERLYING, DXY)
        self.asset_relations(DXY,ETF,VIX_SYMBOLS,COMM)
        return self._df

    def basic_metrics(self, dataframe, *args):
        # dataframe = (dataframe.sort_index())  #sorting from the oldest on the top to the newest on the bottom, most of the fuction in pandas expect that the previous row is the earlierst one
        # columns=list(dataframe.columns)
        dataframe = dataframe.join(self._df, how="inner")
        print(dataframe.head(10))
        for arg in args:
            for symbol in arg.values():

                self._df[f"{symbol}_return_1"] = dataframe[symbol].pct_change(1)
                self._df[f"{symbol}_return_5"] = dataframe[symbol].pct_change(5)
                self._df[f"{symbol}_return_10"] = dataframe[symbol].pct_change(10)
                # self._df[f"{symbol}_return_20"] = price_lag.pct_change(20)
                # self._df[f"{symbol}_return_30"] = price_lag.pct_change(30)
                # self._df[f"{symbol}_return_50"] = price_lag.pct_change(50)

                # self._df[f"{symbol}_momentum_ratio"] = self._df[f"{symbol}_return_5"] / self._df[f"{symbol}_return_20"]
                # self._df[f"{symbol}_momentum_ratio"] = self._df[f"{symbol}_return_10"] / self._df[f"{symbol}_return_20"]

                # self._df[f"{symbol}_rolling_mean_5"] = self._df[f"{symbol}_return_1"].rolling(5).mean()
                # self._df[f"{symbol}_rolling_mean_10"] = self._df[f"{symbol}_return_1"].rolling(10).mean()
                # self._df[f"{symbol}_rolling_mean_20"] = self._df[f"{symbol}_return_1"].rolling(20).mean()

                # self._df[f"{symbol}_vol_10"] = self._df[f"{symbol}_return_1"].rolling(5).std()
                # self._df[f"{symbol}_vol_30"] = self._df[f"{symbol}_return_1"].rolling(30).std()
                # self._df[f"{symbol}_vola_ratio_10/30"] = self._df[f"{symbol}_vol_10"] / self._df[f"{symbol}_vol_30"]
                # self._df[f"{symbol}_high_vol"] = self._df[f"{symbol}_vol_30"] / self._df[f"{symbol}_vol_30"].rolling(50).mean()

                # rolling_max=price_lag.rolling(20).max()
                # rolling_min=price_lag.rolling(20).min()

                # denom=rolling_max - rolling_min
                # price_pos=(price_lag - rolling_min)/denom

                # # self._df[f"{symbol}_range_position"]=price_pos.where(denom!=0) # tells us where we are  between the min and low
                # '''
                # ~0 → oversold / low
                # ~1 → overbought / high
                # ~0.5 → neutral
                # '''

            print(self._df.tail(20))
        return self._df

    def z_score(self, rolling_window, *args):
        """
        checking the strenght/scale of the 1 day return
        comparing to the latest rolling std. Thanks to this , all the returns are normalized Example :
        return = 1%
         rolling_std = 0.5%
         → resutl = 2.0   ; big movement of the 1 day return

         other example :
         return = 1%
         rolling_std = 3%
         → wynik = 0.33 ; small movement of the 1 day return
        """
        new_zscore_results = {}

        for arg in args:
            for symbol in arg.values():
                series = self._df[f"{symbol}_return_1"]
                roll_std = series.rolling(rolling_window).std()
                roll_std = roll_std.replace(0, np.nan) # in case of  0 replaced to 0, will be easier later to manange it and drop it from dataframe
                print(roll_std)
                print(series)

                new_zscore_results[f"{symbol}_zscore_{rolling_window}"] = series / roll_std

        self._df = pd.concat([self._df, pd.DataFrame(new_zscore_results)], axis=1)
        print(self._df.tail(20))
        return self._df

    def ratios(self, return_window, base_underlying, *args):
        base_underlying = BASE_UNDERLYING.values()
        base_underlying = list(base_underlying)[0]
        for arg in args:
            for value in arg.values():
                self._df[f"{base_underlying}_{value}_spread"] = (
                    self._df[f"{base_underlying}_return_{return_window}"]
                    - self._df[f"{value}_return_{return_window}"]
                )
            return self._df
        
    def asset_relations(self,dxy,etf,vix,comm):
        for symbol_dxy, symbol_vix in product(dxy.values(), vix.values()):
            self._df[f'{symbol_dxy}_x_{symbol_vix}']=self._df[f'{symbol_dxy}_return_10'] *self._df[f'{symbol_vix}_return_10']
        
        for symbol_etf, symbol_vix in product(etf.values(), vix.values()):
            self._df[f'{symbol_etf}_x_{symbol_vix}']=self._df[f'{symbol_etf}_return_10'] *self._df[f'{symbol_vix}_return_10']
        
        for symbol_comm, symbol_dxy in product(comm.values(), dxy.values()):
            self._df[f'{symbol_comm}_x_{symbol_dxy}']=self._df[f'{symbol_comm}_return_10'] *self._df[f'{symbol_dxy}_return_10']
        
        return self._df

    # def correlation_betwee_instrumentss(self, return_window, roll_windonw, *args):
    #     for arg in args:
    #         for arg1, arg2 in itertools.combinations(arg.values(), 2):
    #             if "GOLD" in (arg1, arg2):
    #                 continue
    #             self._df[
    #                 f"corr_{arg1}_{arg2}_ret_windonw_{return_window}_roll_wind_{roll_windonw}"
    #             ] = (
    #                 (self._df[f"{arg1}_return_{return_window}"])
    #                 .rolling(roll_windonw)
    #                 .corr(self._df[f"{arg2}_return_{return_window}"])
    #             )

    # def correlation_betwee_instruments(self, base_underlying, return_window, roll_windonw, *args):
    #     base_underlying = BASE_UNDERLYING.values()
    #     base_underlying = list(base_underlying)[0]
    #     print(base_underlying)
    #     for arg in args:
    #         for value in arg.values():
    #             self._df[
    #                 f"corr_{base_underlying}_{value}_ret_windonw_{return_window}_roll_wind_{roll_windonw}"
    #             ] = (
    #                 (self._df[f"{base_underlying}_return_{return_window}"])
    #                 .rolling(roll_windonw)
    #                 .corr(self._df[f"{value}_return_{return_window}"])
    #             )

    #     return self._df

    # def clean_features(self):
    #     # zamień inf/-inf na NaN

    #     print(np.isinf(self._df).sum())
    #     print(self._df.tail(10))
    #     self._df = self._df.replace([np.inf, -np.inf], np.nan)
    #     self._df.dropna()

    #     # print(np.isinf(self._df).sum())
    #     self._df.replace([np.inf, -np.inf], np.nan, inplace=True)
    #     # wypełnij NaN zerem (lub inną logiką np. średnią kolumny)
    #     # self._df.fillna(0, inplace=True)
    #     self._df.dropna()

    #     return self._df

    # def ratios(self, return_window, base_underlying, *args):
    #     for arg in args:
    #         for value in arg.values():
    #             self._df[f"diff_{base_underlying}_{value}"] = (
    #                 self._df[f"{base_underlying}_return_{return_window}"]
    #                 - self._df[f"{value}_return_{return_window}"]
    #             )
    #             return self._df

    # def ratios2(self, dataframe,underlying):
    #     for col in dataframe.columns:
    #         if col!=underlying:
    #             self._df[f"{underlying}_{col}_return_diff"] = dataframe[underlying].shift(1).pct_change() - dataframe[col].shift(1).pct_change()
    #     return self._df

    # to be removed , I will be taking the spreads from fred directly
    # def spread_between_yields(self, dataframe, US_yield_one, US_yield_two):
    #     us_price_lag_1 = dataframe[US_yield_one].shift(1)
    #     us_price_lag_2 = dataframe[US_yield_two].shift(1)
    #     self._df[f"{US_yield_one}_{US_yield_two}_spread"] = us_price_lag_1 - us_price_lag_2
    #     return self._df

    def dxy_builder(self, dataframe):
        print(dataframe.columns.tolist())
        self._df[f"DXY"] = (
            dataframe["EUR_USD"] ** (-0.576)
            * dataframe["USD_JPY"] ** (0.136)
            * dataframe["GBP_USD"] ** (-0.119)
            * dataframe["USD_CAD"] ** (0.091)
            * dataframe["USD_SEK"] ** (-0.042)
            * dataframe["USD_CHF"] ** (-0.036)
        )

        print(self._df.head(10))

        return self._df

    # def return_calc(self,dataframe,ccy_pair,return_window):
    #         new_df=pd.DataFrame()
    #                 new_df.index=dataframe.index
    #                         price_lag=dataframe[ccy_pair].shift(return_window)
    #                                 new_df[f"{ccy_pair}_return_{return_window}"] = price_lag.pct_change()
    #                                         return new_df

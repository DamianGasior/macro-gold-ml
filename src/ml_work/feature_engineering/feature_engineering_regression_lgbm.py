# from src.pipeline.pipeline import DataPipeline
import itertools
from itertools import product
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

from src.pipeline.utils import (
    SYMBOL_MAPPINGS,
    OTHER,
    BASE_UNDERLYING,
    VIX_SYMBOLS,
    CCY_SYMBOLS,
    RATES,
    REAL_YIELDS,
    ETF,
    COMM,
    RATE_DIFF,
    INFL_EXP,
    CPI,
    CRYPTOS,
    DXY,
    ECONOMIC_SENTIMENT,
)


class FeatureRegressionEngineeringLGBMR:
    def __init__(self):
        self._df = pd.DataFrame()

    @property
    def return_dataframe(self) -> pd.DataFrame:
        return self._df

    def feature_enginerring_pipeline(self, dataframe):
        df = dataframe

        dataframe_dxy = self.dxy_builder(dataframe)
        self._df = self.dataframe_join_builder(dataframe_dxy, df)

        self._df = self.basic_metrics(VIX_SYMBOLS, ETF, COMM, DXY, BASE_UNDERLYING)
        self._df = self.basic_metrics2(ECONOMIC_SENTIMENT)

        # self.z_score(20, ETF, COMM,DXY,BASE_UNDERLYING)     # does not work well for
        # self._df=self.dataframe_join_builder(self._df,z_score)

        # self.ratios(1, BASE_UNDERLYING, DXY)
        # self.asset_relations(DXY,REAL_YIELDS,VIX_SYMBOLS,BASE_UNDERLYING,COMM,ETF)

        return self._df

    def one_day_retun(self, symbol):
        price = self._df[symbol]
        log_ret = np.log(price).diff()
        returns = log_ret.shift(1)
        return returns

    #

    def basic_metrics(self, *args):
        # dataframe=dataframe_input.copy()
        print(self._df.columns)
        self._df = self._df.sort_index()
        for arg in args:
            for symbol in arg.values():

                shifted_price = self._df[symbol].shift(1)

                self._df[f"{symbol}_return"] = shifted_price.pct_change()
                self._df[f"{symbol}_return_5"] = shifted_price.pct_change(5)
                self._df[f"{symbol}_return_10"] = shifted_price.pct_change(10)
                self._df[f"{symbol}_return_20"] = shifted_price.pct_change(20)
                self._df[f"{symbol}_return_30"] = shifted_price.pct_change(30)

                # mean_reversion, where the price stands to the n rolling(n).mean
                # self._df[f"{symbol}_mean_revr_10"] = (shifted_price / shifted_price.rolling(10).mean())
                # self._df[f"{symbol}_mean_revr_20"] = (shifted_price / shifted_price.rolling(20).mean())
                # self._df[f"{symbol}_mean_revr_30"] = (shifted_price / shifted_price.rolling(30).mean())

                # volatility is measured on returns
                return_1 = shifted_price.pct_change(1)
                self._df[f"{symbol}_vol_10"] = return_1.rolling(10).std()
                self._df[f"{symbol}_vol_20"] = return_1.rolling(20).std()
                self._df[f"{symbol}_vol_30"] = return_1.rolling(30).std()

                # price / rolling average , if >0 , price is above average = uptrend ; if <0 , price is below average = downtrend
                self._df[f"{symbol}_trend_regime_10"] = (
                    shifted_price / shifted_price.rolling(10).mean()
                )

                self._df[f"{symbol}_trend_regime_20"] = (
                    shifted_price / shifted_price.rolling(20).mean()
                )
                self._df[f"{symbol}_trend_regime_20"] = (
                    shifted_price / shifted_price.rolling(20).mean()
                )
                self._df[f"{symbol}_trend_regime_30"] = (
                    shifted_price / shifted_price.rolling(30).mean()
                )

                # MACD Signal
                macd_line = (
                    shifted_price.ewm(span=12, adjust=False).mean()
                    - shifted_price.ewm(span=26, adjust=False).mean()
                )
                singal = macd_line.ewm(span=9, adjust=False).mean()
                self._df[f"{symbol}_macd_singal_12_26__9"] = macd_line - singal

                print(self._df[f"{symbol}_macd_singal_12_26__9"])

                # mean_reversion, where the price stands to the n rolling(n).mean
                # self._df[f"{symbol}_mean_norm_10"] = (shifted_price - shifted_price.rolling(10).mean())/shifted_price.rolling(10).std()
                # self._df[f"{symbol}_mean_norm_20"] = (shifted_price - shifted_price.rolling(20).mean())/shifted_price.rolling(20).std()
                # self._df[f"{symbol}_mean_norm_30"] = (shifted_price - shifted_price.rolling(30).mean())/shifted_price.rolling(30).std()

                # momentum

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

        # the below does not work well for classfication model
        # shifted_spy=self._df['SPY'].shift(1)
        # self._df[f"SPY_risk_on_20"] = shifted_spy / shifted_spy.rolling(20).mean()
        inf_count = np.isinf(self._df).sum()
        print(inf_count[inf_count > 0])
        inf_count2 = np.isnan(self._df).sum()
        print(inf_count2[inf_count2 > 0])
        self._df = self._df.replace([np.inf, -np.inf], np.nan)

        return self._df

    def basic_metrics2(self, *args):
        # dataframe=dataframe_input.copy()
        print(self._df.columns)
        self._df = self._df.sort_index()
        for arg in args:
            for symbol in arg.values():

                shifted_price = self._df[symbol].shift(1)

                # mean_reversion, where the price stands to the n rolling(n).mean
                self._df[f"{symbol}_mean_roll_10"] = shifted_price.rolling(10).mean()
                self._df[f"{symbol}_mean_roll_20"] = shifted_price.rolling(20).mean()
                self._df[f"{symbol}_mean_roll_30"] = shifted_price.rolling(30).mean()

                # volatility is measured on returns

                # price / rolling average , if >0 , price is above average = uptrend ; if <0 , price is below average = downtrend
                self._df[f"{symbol}_trend_regime_20"] = (
                    shifted_price / shifted_price.rolling(20).mean()
                )
                self._df[f"{symbol}_trend_regime_20"] = (
                    shifted_price / shifted_price.rolling(20).mean()
                )
                self._df[f"{symbol}_trend_regime_30"] = (
                    shifted_price / shifted_price.rolling(30).mean()
                )

        inf_count = np.isinf(self._df).sum()
        print(inf_count[inf_count > 0])
        inf_count2 = np.isnan(self._df).sum()
        print(inf_count2[inf_count2 > 0])
        self._df = self._df.replace([np.inf, -np.inf], np.nan)

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
        z_score_df = pd.DataFrame()
        for arg in args:
            for symbol in arg.values():
                ret = self._df[symbol].pct_change()
                new_zscore_results[f"{symbol}_zscore_{rolling_window}"] = (
                    ret.shift(1) / ret.shift(1).rolling(rolling_window).std()
                )

        z_score_df = pd.concat([pd.DataFrame(new_zscore_results)], axis=1)
        self._df = self._df.join(z_score_df, how="left")

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

    def asset_relations(self, dxy, real_rate, vix, benchmark, comm, etf):
        # for symbol_dxy, symbol_vix in product(dxy.values(), vix.values()):
        #     self._df[f'{symbol_dxy}_x_{symbol_vix}']=self._df[f'{symbol_dxy}_return_10'] *self._df[f'{symbol_vix}_return_10']

        # for symbol_etf, symbol_vix in product(etf.values(), vix.values()):
        #     self._df[f'{symbol_etf}_x_{symbol_vix}']=self._df[f'{symbol_etf}_return_10'] *self._df[f'{symbol_vix}_return_10']

        for symbol_bench, symbol_dxy in product(benchmark.values(), dxy.values()):
            self._df[f"{symbol_bench}_ret_vs_{symbol_dxy}_ret__5"] = self._df[
                f"{symbol_bench}"
            ].pct_change(5).shift(1) - self._df[f"{symbol_dxy}"].pct_change(5).shift(1)
            self._df[f"{symbol_bench}_ret_vs_{symbol_dxy}_ret__10"] = self._df[
                f"{symbol_bench}"
            ].pct_change(10).shift(1) - self._df[f"{symbol_dxy}"].pct_change(10).shift(1)

        # print(self._df.columns)

        for symbol_bench, symbol_comm in product(benchmark.values(), etf.values()):
            self._df[f"{symbol_bench}_ret_vs_{symbol_comm}_ret__5"] = self._df[
                f"{symbol_bench}"
            ].pct_change(5).shift(1) - self._df[f"{symbol_comm}"].pct_change(5).shift(1)
            self._df[f"{symbol_bench}_ret_vs_{symbol_comm}_ret__10"] = self._df[
                f"{symbol_bench}"
            ].pct_change(10).shift(1) - self._df[f"{symbol_comm}"].pct_change(10).shift(1)

        return self._df

    def dxy_builder(self, dataframe_raw):
        new_df_dxy = pd.DataFrame()
        logger.debug(f"dataframe used in dxy_builder are: {dataframe_raw}")
        logger.debug(f"dataframe type is : {type(dataframe_raw)}")
        new_df_dxy[f"DXY"] = (
            dataframe_raw["EUR_USD"] ** (-0.576)
            * dataframe_raw["USD_JPY"] ** (0.136)
            * dataframe_raw["GBP_USD"] ** (-0.119)
            * dataframe_raw["USD_CAD"] ** (0.091)
            * dataframe_raw["USD_SEK"] ** (-0.042)
            * dataframe_raw["USD_CHF"] ** (-0.036)
        )
        logger.debug(f"new_df_dxy returned  in dxy_builder is: {new_df_dxy}")
        return new_df_dxy

    def dataframe_join_builder(self, df1, df2):
        joined_df = df1.join(df2, how="left")
        return joined_df

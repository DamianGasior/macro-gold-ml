import numpy as np
import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


def calculate_cagr(dataframe, column_name):
    df = dataframe[column_name].dropna()
    trading_years = (df.index[-1] - df.index[0]).days / 365
    cagr = (df.iloc[-1] / df.iloc[0]) ** (1 / trading_years) - 1
    logger.debug(f"CAGR : {cagr}")


def drawdown_from_peak(dataframe, column_name):
    df = dataframe[column_name].dropna()
    cum_max = df.cummax()
    drawdown = (df - cum_max) / cum_max
    logger.debug(f"drawdown is : {drawdown.min()} ")


def buy_and_hold_strateg(dataframe, column_name):
    # this method calcualtes what is the return when you buy  and hold comparing to the ML strategy
    start_price = dataframe[column_name].iloc[0]
    end_price = dataframe[column_name].iloc[-1]
    buy_hold = end_price / start_price - 1
    logger.debug(f"buy_hold returns is  : {buy_hold:.3%}")


def return_std(dataframe, column_name):
    returns = dataframe[column_name]
    returns = returns.dropna()
    return_std = returns.std()
    logger.debug(f"stand deviation is {return_std}")
    vol_annual = return_std * np.sqrt(252)
    logger.debug(f"vol_annual is {vol_annual}")

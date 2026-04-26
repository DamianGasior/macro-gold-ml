import numpy as np
import pandas as pd
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s", force=True
)

logger = logging.getLogger(__name__)


def calculate_cagr(dataframe, column_name):
    df = dataframe[column_name].dropna()
    trading_years = (df.index[-1] - df.index[0]).days / 365
    cagr = (df.iloc[-1] / df.iloc[0]) ** (1 / trading_years) - 1
    logger.debug(f"CAGR (compoound annual growth range) : {cagr:.3%}")
    print(cagr)
    return cagr


def drawdown_from_peak(dataframe, column_name):
    df = dataframe[column_name].dropna()
    cum_max = df.cummax()
    drawdown = (df - cum_max) / cum_max
    min_drawd = (drawdown.min())
    logger.debug(f"Drawdown is : {min_drawd:.3%} ")


def buy_and_hold_strateg(dataframe, column_name):
    # this method calcualtes what is the return when you buy  and hold comparing to the ML strategy
    start_price = dataframe[column_name].iloc[0]
    end_price = dataframe[column_name].iloc[-1]
    buy_hold = end_price / start_price - 1
    logger.debug(f"BUY and HOLD returns is  : {buy_hold:.3%}; basically your return starting from trade date at trade price till today(latest available data)")


def return_std(dataframe, column_name):
    returns = dataframe[column_name]
    returns = returns.dropna()
    return_std = returns.std()
    logger.debug(f"Stand deviation is {return_std:.3%}")
    vol_annual = return_std * np.sqrt(252)
    logger.debug(f"Vol_annual is {vol_annual:.3%}")

def dates_numbers(dataframe,column_name):
    logger.debug(f"Number of na's: {dataframe[column_name].isna().sum()}")
    logger.debug(f'First date of the reviewed dataframe: {dataframe[column_name].index[1]}')
    logger.debug(f'Last date of the reviewed dataframe: {dataframe[column_name].index[-1]}')
    logger.debug(f'First date to be considered as no trade or trade: {dataframe[column_name].first_valid_index()}')
    logger.debug(f'Last date to be considered as no trade or trade: {dataframe[column_name].last_valid_index()}')
    counts2=dataframe[column_name].value_counts()
    counts_true=counts2[1.0]
    counts_false=counts2[0.0]
    logger.debug(f"Number of trades executed : {counts_true}. Number of trades not exeucted: {counts_false} (being below the threshold)")







  
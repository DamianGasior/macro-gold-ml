import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def calculate_cagr(dataframe, column_name):
    logger.debug(f"dataframe used in cagr are: {dataframe}")
    logger.debug(f"dataframe type is : {type(dataframe)}")
    df = dataframe[column_name].dropna()
    trading_years = (df.index[-1] - df.index[0]).days / 365
    cagr = (df.iloc[-1] / df.iloc[0]) ** (1 / trading_years) - 1
    logger.debug(f"CAGR (compoound annual growth range) : {cagr:.3%}")
    return cagr


def drawdown_from_peak(dataframe, column_name):
    df = dataframe[column_name].dropna()
    cum_max = df.cummax()
    drawdown = (df - cum_max) / cum_max
    min_drawd = drawdown.min()
    return min_drawd


def buy_and_hold_strateg(dataframe, column_name):
    # this method calcualtes what is the return when you buy  and hold comparing to the ML strategy
    start_price = dataframe[column_name].iloc[0]
    end_price = dataframe[column_name].iloc[-1]
    buy_hold = end_price / start_price - 1
    logger.debug(
        f"BUY and HOLD returns is  : {buy_hold:.3%}; basically your return starting from trade date at trade price till today(latest available data)"
    )
    return buy_hold


def return_std(dataframe, column_name):
    returns = dataframe[column_name]
    returns = returns.dropna()
    return_std = returns.std()
    logger.info(f"Stand deviation is {return_std:.3%}")
    vol_annual = return_std * np.sqrt(252)
    logger.info(f"Vol_annual is {vol_annual:.3%}")
    return vol_annual


def sharpe_calc(returns, number_of_days):
    logger.debug(f"Returns used in sharpe are: {returns}")
    logger.debug(f"Returns type is : {type(returns)}")
    sharpe = (returns.mean() / returns.std()) * np.sqrt(number_of_days)
    return sharpe


def trend_calc(dataframe, column_name, df_timeframe):
    dataframe = dataframe.reindex(df_timeframe.index)
    logger.debug(dataframe[column_name])
    last = dataframe[column_name].iloc[-1]
    logger.debug(last)
    first = dataframe[column_name].iloc[0]
    logger.debug(first)

    if pd.isna(last):
        last = dataframe[column_name].dropna().iloc[-1]

    logger.debug(last)
    column_name_trend = last / first - 1
    logger.debug(column_name_trend)
    return column_name_trend


def find_start_end_date(data_file):
    first_date = data_file.index[0]
    latest_date = data_file.index[-1]
    return first_date, latest_date


def dates_numbers(dataframe, column_name):
    logger.info(f"Number of na's: {dataframe[column_name].isna().sum()}")
    logger.info(f"First date of the reviewed dataframe: {dataframe[column_name].index[1]}")
    logger.info(f"Last date of the reviewed dataframe: {dataframe[column_name].index[-1]}")
    logger.info(
        f"First date to be considered as no trade or trade: {dataframe[column_name].first_valid_index()}"
    )
    logger.info(
        f"Last date to be considered as no trade or trade: {dataframe[column_name].last_valid_index()}"
    )
    counts2 = dataframe[column_name].value_counts()
    logger.info(f"counts2: {counts2}")

    try:
        counts_true = counts2[1.0]
    except KeyError:
        counts_true = 0

    try:
        counts_false = counts2[0.0]
    except KeyError:
        counts_false = 0

    logger.info(
        f"Number of trades executed : {counts_true}. Number of trades not exeucted: {counts_false} (being below the threshold)"
    )


def enforce_non_overlapping_signals(trade_signal: pd.Series, holding_period: int) -> pd.Series:
    """
    Zero's all new signals until the current position is open.
    Thanks to that, we got the guarantee that we have only one position open.
    """
    signal = trade_signal.copy()
    logger.debug(f"incoming signal : {signal}")

    days_until_free = 0

    for i in range(len(signal)):
        if days_until_free > 0:
            signal.iloc[i] = 0  # pozycja wciąż otwarta -> ignoruj nowy sygnał
            days_until_free -= 1
        elif signal.iloc[i] == 1:
            days_until_free = holding_period - 1  # otwieramy pozycję, blokujemy kolejne 9 dni

    logger.debug(f"outoging signal : {signal}")
    return signal

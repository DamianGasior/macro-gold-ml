import numpy as np
import pandas as pd


def calculate_cagr(dataframe,column_name):
    df=dataframe[column_name].dropna()
    trading_years=(df.index[-1]-df.index[0]).days/365
    cagr=(df.iloc[-1]/df.iloc[0])**(1/trading_years)-1
    print(f'CAGR : {cagr}')


def drawdown_from_peak(dataframe,column_name):
    df=dataframe[column_name].dropna()
    cum_max = df.cummax()
    drawdown = (df - cum_max) / cum_max
    print('drawdown is : ', drawdown.min())

def buy_and_hold_strateg(dataframe,column_name):
    # this method calcualtes what is the return when you buy  and hold comparing to the ML strategy
    start_price= dataframe[column_name].iloc[0]
    end_price= dataframe[column_name].iloc[-1]
    buy_hold=end_price/start_price - 1
    print(f'buy_hold returns is  : {buy_hold:.3%}')

def return_std(dataframe,column_name):
    returns=dataframe[column_name]
    returns=returns.dropna()
    return_std=returns.std()
    print(f'stand deviation is {return_std}')
    vol_annual=return_std*np.sqrt(252)
    print(f'vol_annual is {vol_annual}')


    


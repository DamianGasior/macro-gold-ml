import numpy as np

BASE_UNDERLYING = {
    "GLD": "GOLD",
}

OTHER = {"WALCL": "US_TotalAssets"}

CRYPTOS = {"BTC/USD": "Bitcoin"}

VIX_SYMBOLS = {
    "VIXCLS": "CBOE_VIX",
    # "GVZCLS": "GOLD_VIX",
    # "VXVCLS": "CBOE_VIX_3M_S&P500",
    # "OVXCLS": "VIX_ON_OIL",
    # "VXTYN": "VIX_OM_US10Y",
}


CCY_SYMBOLS = {
    "DEXSDUS": "USD_SEK",
    "DEXCAUS": "USD_CAD",
    "DEXUSEU": "EUR_USD",
    # "DEXCHUS": "CNH_USD",
    "DEXUSUK": "GBP_USD",
    "DEXSZUS": "USD_CHF",
    # "DEXHKUS": "HKD_USD",
    "DEXJPUS": "USD_JPY",
}
RATES = {"DGS10": "US10Y", "DGS5": "US5Y", "IR3TIB01USM156N": "US_3M"}

REAL_YIELDS = {"REAINTRATREARAT10Y": "US10Y_Real_IR"}

ETF = {"SPY": "SPY"}

COMM = {"USO": "WTI", "BNO": "BRENT"}

RATE_DIFF = {
    # "AAAFF": "Corp_AAa-FedFundsRate",
    "T10Y2Y": "T10Y2Y",
    # "T10Y3M": "T10Y3M",
    # "T5YFF": "T5YFF",
}

INFL_EXP = {
    "EXPINF1YR": "1Y_INFL_EXPECT",
    "EXPINF2YR": "2Y_IFNL_EXPECT",
    "EXPINF5YR": "5Y_INFL_EXPECT",
    "EXPINF10YR": "10Y_IFNL_EXPECT",
}

CPI = {"CPIAUCSL": "CPI_US"}

SYMBOL_MAPPINGS = {
    # "EUR/USD": "EUR_USD",
    # "UUP" : "UUP",
    "GLD": "GOLD",
    "SPY": "SPY",
    "DGS10": "US10Y",
    "DGS5": "US5Y",
    # "10yply.b": "PL10Y",
    "CPIAUCSL": "CPI_US",
    "IR3TIB01USM156N": "US_3M",
    "REAINTRATREARAT10Y": "US10Y_Real_IR",
    "WALCL": "US_TotalAssets",
    # "EWG" : 'EWG',
    "USO": "WTI",
    "BNO": "BRENT",
    "BTC/USD": "Bitcoin",
    "USEPUINDXD": "EconomicPolicyUncertainty",
    # "VIXY" : "ShortTermVolat",
    #  "VIXY" : "MediumTermVolat",
    "VIXCLS": "CBOE_VIX",
    # "GVZCLS": "GOLD_VIX",
    "VXVCLS": "CBOE_VIX_3M_S&P500",
    "OVXCLS": "VIX_ON_OIL",
    "VXTYN": "VIX_OM_US10Y",
    "AAAFF": "Corp_AAa-FedFundsRate",
    "T10Y2Y": "T10Y2Y",
    "T10Y3M": "T10Y3M",
    "T5YFF": "T5YFF",
    "EXPINF1YR": "1Y_INFL_EXPECT",
    "EXPINF2YR": "2Y_IFNL_EXPECT",
    "EXPINF5YR": "5Y_INFL_EXPECT",
    "EXPINF10YR": "10Y_IFNL_EXPECT",
    "DEXUSEU": "EUR_USD",
    # "DEXCHUS": "CNH_USD",
    "DEXUSUK": "GBP_USD",
    "DEXSZUS": "USD_CHF",
    # "DEXHKUS": "HKD_USD",
    "DEXJPUS": "USD_JPY",
    "DEXSDUS": "USD_SEK",
    "DEXCAUS": "USD_CAD",
    "USEPUINDXD" : "EconomicPolicyUncertainty",
    "INFECTDISEMVTRACKD": "InfectiousDiseaseTracker"
}

DXY = {"DXY" : "DXY"}

ECONOMIC_SENTIMENT = {
    "USEPUINDXD" : "EconomicPolicyUncertainty",
    "INFECTDISEMVTRACKD": "InfectiousDiseaseTracker"


}





# https://fred.stlouisfed.org/categories/32455
# https://fred.stlouisfed.org/categories/32455?t=projection&ob=pv&od=desc

# https://fred.stlouisfed.org/categories/33446

# https://fred.stlouisfed.org/categories/33446?t=yield%20curve&ob=pv&od=desc

# https://fred.stlouisfed.org/series/AAAFF
# przydaloby sie jeszcze zadluzenie USA i  i PKB za ten sam okres

# zobaczyc czy maja jakies  podbne dane do EUR

# to jest super > volaitlity zamiast etf : https://fred.stlouisfed.org/series/VIXCLS

# https://fred.stlouisfed.org/series/AAAFF

# poszukac move index


@staticmethod
def clean_features(*args):
    # zamień inf/-inf na NaN
    for dataframe in args:

        print(np.isinf(dataframe).sum())
        print(dataframe.tail(10))
        dataframe = dataframe.replace([np.inf, -np.inf], np.nan)
        dataframe.dropna()

        # print(np.isinf(self._dataframe).sum())
        dataframe.replace([np.inf, -np.inf], np.nan, inplace=True)
        # wypełnij NaN zerem (lub inną logiką np. średnią kolumny)
        # self._dataframe.fillna(0, inplace=True)
        dataframe.dropna()

    return dataframe

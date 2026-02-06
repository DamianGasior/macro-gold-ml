import pandas as pd


class Data_transformation:
    def __init__(self, api_response, symbol):
        self.api_response = api_response
        self.symbol = symbol

    def to_dataframe(self):
        dataframe = pd.DataFrame(self.api_response)
        dataframe["datetime"]= pd.to_datetime(dataframe["datetime"]) #changing the datetime to type date time
        dataframe.set_index("datetime",inplace=True) # setting datetime as index
        symbol = str(self.symbol)
        dataframe=dataframe.filter(["close"]) #filtering by one column only
        dataframe.rename(columns={"close": symbol}, inplace=True)
        print(dataframe)

        return dataframe


# zaimportuj odpowiedz
# z odpowiedzi, wyciagnij symbol
# wyluskaj potem  dict z danymi z values > stworz dataframe
# w dataframe ustaw date jako indeks
# nastepnie zmien nazwe cen z close na na symbol
# zostaw tylko kolumne gdzie jest symbol (czyli twoj close)

#

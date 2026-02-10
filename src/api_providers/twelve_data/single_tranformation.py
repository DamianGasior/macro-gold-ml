import pandas as pd
from ...pipeline.base_single_transformer import BaseDataTransformer


class Data_transformation(BaseDataTransformer):
    def __init__(self, api_response, symbol):
        self.api_response = api_response
        self.symbol = symbol
        self.dataframe = pd.DataFrame()

    def to_dataframe(self):
        dataframe = pd.DataFrame(self.api_response)
        print(type(dataframe))
        dataframe["datetime"] = pd.to_datetime(
            dataframe["datetime"]
        )  # changing the datetime to type date time
        dataframe.set_index("datetime", inplace=True)  # setting datetime as index
        dataframe = dataframe.filter(["close"])  # filtering by one column only
        dataframe.rename(columns={"close": self.symbol}, inplace=True)
        dataframe = dataframe.apply(
            pd.to_numeric, errors="coerce"
        )  # transform input data from the df to numeric values, if it can not be transfromed to numeric, then it popualted NaN
        dataframe = dataframe.dropna()  # it drops from the row above all NaN rows
        print(dataframe)
        print(type(dataframe))
        self.dataframe = dataframe
        print(type(self.dataframe))
        return self.dataframe

    def return_dataframe(self):
        return self.dataframe

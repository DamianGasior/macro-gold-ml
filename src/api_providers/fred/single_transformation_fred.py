import pandas as pd
from ...pipeline.base_single_transformer import BaseDataTransformer
from src.api_providers.common_df_merger.multiple_dataframe_transformer import (
    Multiple_df_manager,
)


class Data_fred_transformation(BaseDataTransformer):
    def __init__(self, api_response, symbol):
        self.api_response = api_response
        self.symbol = symbol
        self.dataframe = pd.DataFrame()
        self.date_index_max: pd.Timestamp | None = None
        self.date_index_min_max_symbol = {} # zrobic z tego liste globalna, tak by moc potem sprawdzic co i jak 

    # dodac dict ( gdzie beda zapisywane wszedize max   i min daty dla danego symbolu )

    # pierw zrivuc return property i dac print , zoabczycmy co wyjdzie 

    def to_dataframe(self):
        dataframe = pd.DataFrame(self.api_response)
        dataframe["date"] = pd.to_datetime(
            dataframe["date"]
        )  # changing the datetime to type date time
        dataframe.set_index("date", inplace=True)  # setting datetime as index
        symbol = str(self.symbol)
        dataframe = dataframe.filter(["value"])  # filtering by one column only
        dataframe.rename(columns={"value": symbol}, inplace=True)
        print(dataframe.head(10))
        print(dataframe.index.dtype)
        if self.date_index_max is None:
            self.date_index_max = dataframe.index.max()
        elif self.date_index_max is not None:
            max_value = dataframe.index.max()
            if max_value > self.date_index_max:
                self.date_index_max = max_value
            else:
                self.date_index_max

        dataframe = dataframe.apply(
            pd.to_numeric, errors="coerce"
        )  # transform input data from the df to numeric values, if it can not be transfromed to numeric, then it popualted NaN
        dataframe = dataframe.dropna()  # it drops from the row above all NaN rows
        if self.symbol in (
            "IRLTLT01PLM156N",
            "REAINTRATREARAT10Y",
            "CPIAUCSL",
            "IR3TIB01USM156N",
            "WALCL",
            "EXPINF1YR",
            "EXPINF2YR",
            "EXPINF5YR",
            "EXPINF10YR",
        ):
            dataframe = dataframe.resample(
                "B"
            ).ffill()  # new dataframe, new index - new dates,  inthis case 'B' indicates Business days calendar, and forward fill.
            print(dataframe)
            self.dataframe = dataframe
        # elif self.symbol in ( 'IRLTLT01PLM156N',"REAINTRATREARAT10Y",'CPIAUCSL','CPHPTT01PLM659N','IR3TIB01USM156N',"IR3TIB01USM156N","IR3TIB01PLM156N"):

        else:
            self.dataframe = dataframe
            # dataframe=dataframe.resample('B').ffill()

        # if self.symbol in ("DEXCHUS", "DEXSZUS", "DEXHKUS", "DEXJPUS", "DEXSDUS", "DEXCAUS"):
        #     print(dataframe.head(10))
        #     self.dataframe[self.symbol] = 1 / self.dataframe[self.symbol]
        #     print(dataframe.head(10))

        print(self.dataframe.head(10))
        print(self.dataframe.tail(10))

        self.date_index_min_max_symbol[symbol] = [
            {"min": dataframe.index.min()},
            {"max": dataframe.index.max()},
        ]

        print(self.date_index_min_max_symbol)

        dataframe_normalized=Multiple_df_manager.normalize_df(dataframe)
        self.dataframe = dataframe_normalized

        return self.dataframe

    def return_dataframe(self):
        return self.dataframe

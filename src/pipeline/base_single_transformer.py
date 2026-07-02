from abc import ABC, abstractmethod


class BaseDataTransformer(ABC):

    @abstractmethod
    def to_dataframe(self):
        # creates a dataframe
        # is changing the index tformat to pd.to_datetime(dataframe.index)
        # renaming the column index so that is the same accross all df from all data providers
        # renaming the column for valclosing prices / quotes  with the underlying symbol
        # filtering the df by only one column with the price / quote
        # changing the values of those columns to numerical values by applying :
        # dataframe=dataframe.apply(pd.to_numeric,errors='coerce')
        # droping all the Na
        # returning self.dataframe

        pass

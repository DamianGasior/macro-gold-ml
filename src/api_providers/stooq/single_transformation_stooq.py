import pandas as pd
from ...pipeline.base_single_transformer import BaseDataTransformer



class Data_stooq_transformation(BaseDataTransformer):
    def __init__(self,api_reponse,symbol):
        self.api_reponse=api_reponse
        self.symbol=symbol
        self.dataframe=pd.DataFrame()


    def to_dataframe(self):

        dataframe=pd.DataFrame(self.api_reponse)
        print(type(dataframe))

        print(type(dataframe))  # 
        # dataframe.set_index('Data', inplace=True)
        dataframe.index = pd.to_datetime(dataframe.index)
        dataframe.rename(columns={"Data": 'datetime'}, inplace=True)
        dataframe=dataframe.filter(["Zamkniecie"])
        dataframe.rename(columns={"Zamkniecie": self.symbol}, inplace=True)
        dataframe=dataframe.apply(pd.to_numeric,errors='coerce')
        dataframe=dataframe.dropna()
        # print(dataframe)
        self.dataframe=dataframe
        return self.dataframe
    
    def return_dataframe(self):
        return self.dataframe





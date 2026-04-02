import pandas as pd
from ...pipeline.base_single_transformer import BaseDataTransformer



class Data_fred_transformation(BaseDataTransformer):
    def __init__(self, api_response, symbol):
        self.api_response = api_response
        self.symbol = symbol
        self.dataframe=pd.DataFrame()
        


    def to_dataframe(self):
        dataframe = pd.DataFrame(self.api_response)
        dataframe["date"]= pd.to_datetime(dataframe["date"]) #changing the datetime to type date time
        dataframe.set_index("date",inplace=True) # setting datetime as index
        symbol = str(self.symbol)
        dataframe=dataframe.filter(["value"]) #filtering by one column only
        dataframe.rename(columns={"value": symbol}, inplace=True)
        dataframe=dataframe.apply(pd.to_numeric, errors='coerce') #transform input data from the df to numeric values, if it can not be transfromed to numeric, then it popualted NaN
        dataframe=dataframe.dropna() #it drops from the row above all NaN rows
        if self.symbol in ( 'IRLTLT01PLM156N','CPIAUCSL','CPHPTT01PLM659N','IR3TIB01USM156N',"IR3TIB01USM156N","IR3TIB01PLM156N"):
            dataframe=dataframe.resample('B').ffill() # new dataframe, new index - new dates,  inthis case 'B' indicates Business days calendar, and forward fill. 
            print(dataframe)
            self.dataframe = dataframe
        else:
            self.dataframe=dataframe
            
        print(dataframe)
        print(type(self.dataframe))
        return self.dataframe
    
    def return_dataframe(self):
        return self.dataframe
    

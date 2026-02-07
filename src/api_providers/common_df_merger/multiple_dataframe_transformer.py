import logging
import sys
from src.api_providers.twelve_data.single_tranformation import Data_transformation
import pandas as pd


class Multiple_df_manager:
    def __init__(self, concact_fx_df:pd.DataFrame | None = None):
        self.fx_list = []
        self.bond_yield_list = []
        self.concact_fx_df=concact_fx_df

    def add_to_fx_list(self, passed_fx_df):
        print(type(self.fx_list))
        self.fx_list.append(passed_fx_df)
        return self.fx_list

    def add_to_bond_yield_list(self, passed_bond_yield_df):
        self.bond_yield_list.append(passed_bond_yield_df)
        return self.bond_yield_list

    def len_of_lists(self):
        print(f"Length of fx_list is {len(self.fx_list)}")

    # concacenating dataframes which were passed as dataframes,
    # join='inner' helps to merge only with the common index, there are no NaN applied in case of mismatch
    # axis 1 = merging by columns
    

    def list_concacenate(self,param):
        if param == 'fx':
            # print(type())
            print(len(self.fx_list))
            
            conc_df = pd.concat(self.fx_list, axis=1, join="inner")
            print(type(conc_df))
        elif param == 'bond_yeld':
            conc_df = pd.concat(self.fx_list, axis=1, join="inner")
        print(type(conc_df))
        self.concact_fx_df=conc_df
        return self.concact_fx_df


    def return_list(self):
        return self.fx_list
    
    def return_df(self):
        return self.concact_fx_df


    

import logging
import sys
from src.api_providers.twelve_data.single_tranformation import Data_transformation
import pandas as pd


class Multiple_df_manager:
    def __init__(self, concact_df: pd.DataFrame | None = None):
        self.df_passed_list = []
        self.concact_df = concact_df

    @property
    def return_df(self):
        return self.concact_df

    def add_to_working_list(self, passed_df):
        # print(type(passed_df))
        self.df_passed_list.append(passed_df)
        return self.df_passed_list

    def len_of_lists(self):
        print(f"Length of fx_list is {len(self.fx_list)}")

    # concacenating dataframes which were passed as dataframes,
    # join='inner' helps to merge only with the common index, there are no NaN applied in case of mismatch
    # axis 1 = merging by columns

    def list_concacenate(self):
        # for i, df in enumerate(self.df_passed_list): # for debugging purpose
        #     print(i, df.shape)
        #     print(df.index.min(), df.index.max())

        conc_df = pd.concat(self.df_passed_list, axis=1, join="inner")

        # print("RESULT SHAPE:", conc_df.shape)  # for dbuggin purpose
        self.concact_df = conc_df
        return self.concact_df

    def df_concacenate(self, *args):
        df_list = []
        for df in args:
            df_list.append(df)
        self.concact_df = pd.concat(df_list, axis=1, join="inner")
        return self.concact_df

    def return_list(self):
        return self.fx_list

    def multiple_df_manager_pipeline(self, passed_df):
        self.add_to_working_list(passed_df)
        self.list_concacenate()

import pandas as pd
import numpy as np


class Multiple_df_manager:
    def __init__(self, concact_df: pd.DataFrame | None = None):
        self.df_passed_list = []
        self.concact_df = concact_df

    @property
    def return_df(self):
        print(type(self.concact_df))
        print(self.concact_df.dtypes)
        print(self.concact_df.info())
        print(self.concact_df.head(50))
        # print(isinstance(self.concact_df,Multiple_df_manager))
        # self.concact_df=Multiple_df_manager.normalize_df(self.concact_df)
        assert self.concact_df.index.is_monotonic_increasing, "Index is not sorted!"
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

    def list_concacenate(self):  # this is a conct of df's'
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
        
        self.concact_df = pd.concat(df_list, axis=1, join="inner")  # joining those dataframes which have the same dates
        return self.concact_df

    def return_list(self):
        return self.fx_list

    def multiple_df_manager_pipeline(self, passed_df):
        self.add_to_working_list(passed_df)
        self.list_concacenate()

    @staticmethod
    def rename_columns_in_df(df: pd.DataFrame, columns_renamed: dict):
        df.rename(columns=columns_renamed, inplace=True)
        print(df.head(10))
        print(df.tail(10))
        return df
    
    @staticmethod
    def normalize_df(dataframe_received):
        df=dataframe_received.copy()
        df=df.sort_index()
        df.index = pd.to_datetime(df.index)
        df = df[~df.index.duplicated(keep="last")] # helps to avoid duplicates
        assert df.index.is_monotonic_increasing, "Index is not sorted!"
        return df

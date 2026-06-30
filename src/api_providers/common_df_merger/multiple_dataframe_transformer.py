import pandas as pd
import numpy as np
import logging


logger = logging.getLogger(__name__)


class Multiple_df_manager:
    def __init__(self, concact_df: pd.DataFrame | None = None):
        self.df_passed_list = []
        self.concact_df = concact_df

    @property
    def df(self):
        assert self.concact_df.index.is_monotonic_increasing, "Index is not sorted!"
        return self.concact_df

    def add_to_working_list(self, passed_df):
        # print(type(passed_df))
        self.df_passed_list.append(passed_df)
        return self.df_passed_list

    # concacenating dataframes which were passed as dataframes,
    # join='inner' helps to merge only with the common index, there are no NaN applied in case of mismatch
    # axis 1 = merging by columns

    def list_concacenate(self):  # this is a conct of df's'
        # conc_df = pd.concat(self.df_passed_list, axis=1, join="inner")
        # two lines below for testing purpose replacing the one above

        conc_df = pd.concat(self.df_passed_list, axis=1, join="outer")
        conc_df = conc_df.ffill()
        logger.debug(f"conc_df. tail is : {conc_df.tail(12)}")
        self.concact_df = conc_df
        return self.concact_df

    def df_concacenate(self, *args):
        df_list = []
        for df in args:
            df_list.append(df)

        self.concact_df = pd.concat(
            df_list, axis=1, join="inner"
        )  # joining those dataframes which have the same dates
        return self.concact_df

    # def return_list(self):
    #     return self.fx_list

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
        df = dataframe_received.copy()
        df = df.sort_index()
        df.index = pd.to_datetime(df.index)
        df = df[~df.index.duplicated(keep="last")]  # helps to avoid duplicates
        assert df.index.is_monotonic_increasing, "Index is not sorted!"
        return df

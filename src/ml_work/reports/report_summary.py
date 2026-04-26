import numpy as np
import pandas as pd
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s",
    force=True,
)

logger = logging.getLogger(__name__)


class Report_Summary:

    def __init__(self):
        self._summarized_results = pd.DataFrame()

    @property
    def return_summarized_results(self):
        return self._summarized_results

    def add_start_end_date(self, count, data_file):
        first_date = data_file.index[0]
        latest_date = data_file.index[-1]

        new_row = pd.DataFrame(
            {"split": [count], "start_date": [first_date], "send_date": [latest_date]}
        )

        self._summarized_results = pd.concat([self._summarized_results, new_row], ignore_index=True)

        print(self._summarized_results.head(10))
        return self._summarized_results

    # def start_end_date_def(self,data_file):
    #     first_date = data_file[1]
    #      # the oldest date of the datafrmae
    #     latest_date = data_file[-1] # latest date of the dataframe
    #     return first_date, latest_date

    def report_pipeline(self, count, data_file):
        self.add_start_end_date(count, data_file)

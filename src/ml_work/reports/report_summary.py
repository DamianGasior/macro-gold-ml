import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class Report_Summary:

    def __init__(self):
        self._summarized_results = pd.DataFrame()
        # self._format_config = {
        #     "cagr": "{:.2%}",
        #     "drawdown": "{:.2%}",
        #     "vol_annual": "{:.2%}",
        #     "sharpe": "{:.4f}"
        # }

    @property
    def summarized_results(self):
        return self._summarized_results

    def show_report(self):
        return self._summarized_results

    def add_to_df(self, incoming_dict):
        if self._summarized_results.empty:
            self._summarized_results = pd.DataFrame([incoming_dict])
        else:
            self._summarized_results.loc[len(self._summarized_results)] = incoming_dict

    def report_pipeline(self, incoming_dict):
        # self.add_start_end_date(count, data_file)
        self.add_to_df(incoming_dict)

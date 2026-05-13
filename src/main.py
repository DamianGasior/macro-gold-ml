# from collections import deque
# from src.api_providers.common_df_merger.multiple_dataframe_transformer import (
#     Multiple_df_manager,
# )
# from src.api_providers.twelve_data.api_request_twelve_data import (
#     Underlying_twelve_data_reuquest,
# )
# from src.api_providers.fred.api_request_fred import Fred_request_api
# from src.api_providers.stooq.api_request_stooq import Stooq_request_api
from src.logging_config import setup_logging
from src.pipeline.pipeline import run_pipeline


def main():
    setup_logging()
    run_pipeline()


if __name__ == "__main__":
    main()

from collections import deque
from src.api_providers.common_df_merger.multiple_dataframe_transformer import (
    Multiple_df_manager,
)
from src.api_providers.twelve_data.api_request_twelve_data import (
    Underlying_twelve_data_reuquest,
)
from src.api_providers.fred.api_request_fred import Fred_request_api
from src.api_providers.stooq.api_request_stooq import Stooq_request_api
from src.pipeline.pipeline import DataPipeline


def main():

    symbol_fx_deque = deque(["USD/PLN", "EUR/USD"])
    while len(symbol_fx_deque) > 0:
        symbol_fx = symbol_fx_deque.popleft()
        provider = Underlying_twelve_data_reuquest(symbol_fx)

        pipeline = DataPipeline(symbol_fx, provider)
        pipeline.run()

    symbol_bond_yield_deque = deque(["DGS10"])
    while len(symbol_bond_yield_deque) > 0:
        symbol_fred = symbol_bond_yield_deque.popleft()
        provider = Fred_request_api(symbol_fred)

        pipeline = DataPipeline(symbol_fred, provider)
        pipeline.run()

    symbol_pl_bond_yield_deque = deque(["10yply.b"])
    while len(symbol_pl_bond_yield_deque) > 0:
        symbol_stooq = symbol_pl_bond_yield_deque.popleft()
        provider = Stooq_request_api(symbol_stooq)

        pipeline = DataPipeline(symbol_stooq, provider)
        pipeline.run()




if __name__ == "__main__":
    main()

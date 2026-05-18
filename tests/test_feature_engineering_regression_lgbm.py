import pandas as pd
import pytest
from src.ml_work.feature_engineering.feature_engineering_regression_lgbm import (
    FeatureRegressionEngineeringLGBMR,
)


def test_dxy_builder():
    # dxy_table = pd.DataFrame()
    test_df = pd.DataFrame(
        {
            "EUR_USD": [1.1698],
            "GBP_USD": [1.3535],
            "USD_CHF": [0.7835],
            "USD_JPY": [157.21],
            "USD_SEK": [9.2806],
            "USD_CAD": [1.3608],
        },
        index=pd.DatetimeIndex(["2024-01-01"]),
    )

    dxy_table = FeatureRegressionEngineeringLGBMR().dxy_builder(test_df)
    assert dxy_table["DXY"].iloc[0] == pytest.approx(1.656522, abs=0.0001)

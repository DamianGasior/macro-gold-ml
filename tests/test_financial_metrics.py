import pandas as pd
import pytest

from src.ml_work.financial_metrics import (
    sharpe_calc,
    drawdown_from_peak,
    return_std,
    calculate_cagr,
)


def test_sharpe_calc():
    test_returns = pd.Series(
        [0.064765, 0.046196, 0.065208, 0.080509, 0.082989, 0.054297, 0.004770, -0.006662, -0.016623]
    )
    test_results = sharpe_calc(test_returns, 252)
    assert isinstance(test_results, float)
    assert test_results == pytest.approx(17.40, abs=0.01)


def test_drawdown_from_peak():
    test_df = pd.DataFrame(
        {"equity_curve": [117.78, 117.09, 116.85, 117.60, 442.09, 429.57, 431.04, 433.25]}
    )
    test_min_drawd = drawdown_from_peak(test_df, "equity_curve")
    assert test_min_drawd == pytest.approx(-0.028320025334207927, abs=0.001)


def test_return_std():
    test_df = pd.DataFrame(
        {
            "vol_annual": [
                0.064765,
                0.046196,
                0.065208,
                0.080509,
                0.082989,
                0.054297,
                0.004770,
                -0.006662,
                -0.016623,
            ]
        }
    )
    test_results = return_std(test_df, "vol_annual")
    assert isinstance(test_results, float)
    assert test_results == pytest.approx(0.603928448121133, abs=0.01)


def test_calculate_cagr():
    test_df = pd.DataFrame(
        {
            "equity_curve": [100, 150],
        },
        index=pd.date_range(start="2024-01-01", periods=2, freq="365D"),
    )
    test_min_drawd = calculate_cagr(test_df, "equity_curve")
    assert test_min_drawd == pytest.approx(0.5, abs=0.001)

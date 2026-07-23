import mlflow
from pathlib import Path

PATH_MLFLOW_DB = Path(__file__).parent / "mlflow.db"
"""
this script was created to trigger it always locally.
python3 ml_flow/ml_flow_export_results.py
"""

"""
This file is reponsible for metrics export into a md file from the last run , form the default catalog [0]
"""

mlflow.set_tracking_uri(f"sqlite:///{PATH_MLFLOW_DB}")
runs_df = mlflow.search_runs(experiment_ids=["0"])  # "0" = default catalog "Default"

# (print(list(runs_df.columns))) # shows all the columns

columns = runs_df[
    [
        "run_id",
        "status",
        "start_time",
        "end_time",
        "tags.mlflow.source.type",
        "tags.mlflow.runName",
        "metrics.classification/accuracy_score",
        "metrics.classification/train_accuracy",
        "metrics.classification/test_accuracy",
        "metrics.classification/log_Loss",
        "metrics.classification/roc_auc",
        "metrics.strategy/average_trade_return_pct",
        "metrics.strategy/pnl_long_pct",
        "metrics.strategy/sharpe",
        "metrics.strategy/sharpe_trade",
        "metrics.strategy/vol_annual_pct",
        "metrics.strategy/cagr_pct",
        "metrics.strategy/drawdown_from_peak_pct",
        "metrics.benchmark/buy_and_hold_return_pct",
        "metrics.benchmark/buy_and_hold_vol_annual_pct",
        "metrics.benchmark/buy_and_hold_cagr_pct",
        "metrics.benchmark/buy_and_hold_drawdown_pct",
    ]
]


markdown_table = columns.to_markdown(index=False)
print(markdown_table)

with open(Path(__file__).parent / "mlflow_metrics_results.md", "w") as f:
    f.write(markdown_table)

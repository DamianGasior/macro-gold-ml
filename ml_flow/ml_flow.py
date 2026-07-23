import mlflow
from pathlib import Path

"""

=================================
To open the report in browser UI , run this locally :

cd /home/damian/projekty/Python/macro-gold-ml
venv/bin/mlflow ui --backend-store-uri sqlite:///ml_flow/mlflow.db --port 5000

You will get a  window  , where you can review the results

"""

PATH_MLFLOW_DB = Path(__file__).parent / "mlflow.db"
mlflow.set_tracking_uri(f"sqlite:///{PATH_MLFLOW_DB}")


def ml_flow__log_param(model, proba_thresh, x_train, x_test):
    """
    This method is responsible for gathering basic information about the model
    """
    mlflow.log_param("Model name", str(type(model).__name__))
    mlflow.log_param("Model details", str(model.get_params()))
    mlflow.log_param("PROBABILITY_THRESHOLD details", proba_thresh)
    mlflow.log_param("train_start:", str(x_train.index.min()))
    mlflow.log_param("train_end:", str(x_train.index.max()))
    mlflow.log_param("test_start:", str(x_test.index.min()))
    mlflow.log_param("test_end:", str(x_test.index.max()))


# Saving ( copying) the artefact file - for example : lgbm_classifier.pkl - to the folder of actual run
def ml_flow__log_artifact(path, model_name):
    mlflow.log_artifact(f"{path}/{model_name}")


# metrics below are stored based on that which are passed to the method
def ml_flow__log_metrics(metric_name, metric_value):
    mlflow.log_metric(metric_name, metric_value)

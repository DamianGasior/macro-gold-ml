import mlflow


def ml_flow__log_param(model, proba_thresh, x_train, x_test):
    mlflow.log_param("Model name", str(type(model).__name__))
    mlflow.log_param("Model details", str(model.get_params()))
    mlflow.log_param("PROBABILITY_THRESHOLD details", proba_thresh)
    mlflow.log_param("train_start:", str(x_train.index.min()))
    mlflow.log_param("train_end:", str(x_train.index.max()))
    mlflow.log_param("test_start:", str(x_test.index.min()))
    mlflow.log_param("test_end:", str(x_test.index.max()))


def ml_flow__log_artifact(path, model_name):
    mlflow.log_artifact(f"{path}/{model_name}")


def ml_flow__log_metrics(metric_name, metric_value):
    mlflow.log_metric(metric_name, metric_value)

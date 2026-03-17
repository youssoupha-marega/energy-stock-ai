"""Tests unitaires pour le pipeline d'entraînement."""

import mlflow
import pandas as pd

from src.energystock_ai.pipelines.training.nodes import train_and_register


def test_train_and_register(tmp_path):
    mlflow.set_tracking_uri(str(tmp_path / "mlruns"))

    dates = pd.date_range("2020-01-01", periods=50, freq="D")
    df = pd.DataFrame(
        {
            "date": dates,
            "ticker": ["NEE"] * len(dates),
            "adj_close": (100 + pd.Series(range(len(dates)))).values,
            "Volume": [1000 + i for i in range(len(dates))],
        }
    )
    df["return"] = df["adj_close"].pct_change()

    result = train_and_register(
        features=df,
        target_ticker="NEE",
        test_size=0.2,
        random_state=42,
        mlflow_experiment_name="test_experiment",
        random_forest={"n_estimators": 10, "max_depth": 2},
    )

    assert "best_model_name" in result
    assert "best_rmse" in result
    assert "best_model_version" in result

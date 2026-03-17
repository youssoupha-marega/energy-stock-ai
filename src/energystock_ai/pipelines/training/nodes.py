"""Nodes pour l'entraînement des modèles et le tracking MLflow."""

from __future__ import annotations

import mlflow
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from tensorflow import keras
from typing import Dict, Tuple


def _split_chronological(df: pd.DataFrame, test_size: float) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = df.sort_values("date")
    cutoff = int(len(df) * (1 - test_size))
    return df.iloc[:cutoff], df.iloc[cutoff:]


def _build_lstm_model(input_shape: Tuple[int, int]) -> keras.Model:
    model = keras.Sequential(
        [
            keras.layers.Input(shape=input_shape),
            keras.layers.LSTM(64, activation="tanh"),
            keras.layers.Dense(1),
        ]
    )
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    return model


def train_and_register(
    features: pd.DataFrame,
    target_ticker: str,
    test_size: float,
    random_state: int,
    mlflow_experiment_name: str,
    random_forest: Dict,
) -> Dict[str, str]:
    """Entraîne plusieurs modèles et enregistre le meilleur dans le registre MLflow.

    Renvoie un dict contenant le meilleur modèle et les métriques associées.
    """

    df = features[features["ticker"] == target_ticker].copy()
    df = df.sort_values("date")
    df["target_return_5d"] = df["return"].shift(-5)
    df = df.dropna(subset=["target_return_5d"]).reset_index(drop=True)

    drop_cols = ["date", "ticker", "adj_close", "return", "target_return_5d"]
    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    y = df["target_return_5d"].values

    X_train_df, X_test_df = _split_chronological(df, test_size)
    X_train = X_train_df.drop(columns=[c for c in drop_cols if c in X_train_df.columns])
    y_train = X_train_df["target_return_5d"].values
    X_test = X_test_df.drop(columns=[c for c in drop_cols if c in X_test_df.columns])
    y_test = X_test_df["target_return_5d"].values

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    mlflow.set_experiment(mlflow_experiment_name)

    runs = []

    # Linear Regression
    with mlflow.start_run(run_name="LinearRegression") as run:
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        preds = model.predict(X_test_scaled)
        rmse = mean_squared_error(y_test, preds, squared=False)
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        mlflow.log_params({"model": "LinearRegression"})
        mlflow.log_metrics({"rmse": rmse, "mae": mae, "r2": r2})
        mlflow.sklearn.log_model(model, "model")

        runs.append({"name": "LinearRegression", "rmse": rmse, "mae": mae, "r2": r2, "run_id": run.info.run_id})

    # Random Forest
    with mlflow.start_run(run_name="RandomForest") as run:
        model = RandomForestRegressor(
            n_estimators=random_forest.get("n_estimators", 200),
            max_depth=random_forest.get("max_depth", 10),
            random_state=random_state,
        )
        model.fit(X_train_scaled, y_train)
        preds = model.predict(X_test_scaled)
        rmse = mean_squared_error(y_test, preds, squared=False)
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        mlflow.log_params({"model": "RandomForest", **random_forest})
        mlflow.log_metrics({"rmse": rmse, "mae": mae, "r2": r2})
        mlflow.sklearn.log_model(model, "model")

        runs.append({"name": "RandomForest", "rmse": rmse, "mae": mae, "r2": r2, "run_id": run.info.run_id})

    # LSTM
    with mlflow.start_run(run_name="LSTM") as run:
        X_train_lstm = X_train_scaled.reshape((X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
        X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))

        model = _build_lstm_model((X_train_lstm.shape[1], X_train_lstm.shape[2]))
        model.fit(
            X_train_lstm,
            y_train,
            epochs=10,
            batch_size=32,
            verbose=0,
            validation_split=0.1,
        )
        preds = model.predict(X_test_lstm).flatten()
        rmse = mean_squared_error(y_test, preds, squared=False)
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        mlflow.log_params({"model": "LSTM"})
        mlflow.log_metrics({"rmse": rmse, "mae": mae, "r2": r2})
        mlflow.keras.log_model(model, "model")

        runs.append({"name": "LSTM", "rmse": rmse, "mae": mae, "r2": r2, "run_id": run.info.run_id})

    best = min(runs, key=lambda r: r["rmse"])
    best_name = best["name"]
    best_run_id = best["run_id"]

    client = mlflow.tracking.MlflowClient()
    model_uri = f"runs:/{best_run_id}/model"

    # Crée un modèle enregistré si nécessaire (idempotent)
    try:
        client.create_registered_model("energystock-best-model")
    except Exception:
        pass

    model_version = client.create_model_version(
        name="energystock-best-model", source=model_uri, run_id=best_run_id
    )
    client.transition_model_version_stage(
        name="energystock-best-model", version=model_version.version, stage="Production"
    )

    return {
        "best_model_name": best_name,
        "best_model_run_id": best_run_id,
        "best_model_version": model_version.version,
        "best_rmse": best["rmse"],
        "best_mae": best["mae"],
        "best_r2": best["r2"],
    }

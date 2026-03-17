"""FastAPI application for serving predictions from the best registered model."""

from datetime import datetime

import mlflow
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="EnergyStock AI", version="0.1.0")


class PredictRequest(BaseModel):
    ticker: str = Field(..., description="Ticker de l'action (ex: NEE)")
    as_of_date: str = Field(..., description="Date de prédiction (YYYY-MM-DD)")


class PredictResponse(BaseModel):
    ticker: str
    rendement_predit_5j: float
    signal: str
    intervalle_confiance: list[float]
    version_modele: str
    as_of_date: str


def _load_features(ticker: str, as_of_date: str) -> pd.DataFrame:
    try:
        df = pd.read_parquet("data/02_intermediate/features.parquet")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier de features introuvable")

    df["date"] = pd.to_datetime(df["date"]).dt.date
    target_date = datetime.fromisoformat(as_of_date).date()
    subset = df[(df["ticker"] == ticker) & (df["date"] == target_date)]
    if subset.empty:
        raise HTTPException(status_code=404, detail="Aucune donnée pour la paire/date demandée")
    return subset


def _load_model() -> mlflow.pyfunc.PyFuncModel:
    return mlflow.pyfunc.load_model("models:/energystock-best-model/Production")


def _get_best_model_version() -> str:
    client = mlflow.tracking.MlflowClient()
    versions = client.get_latest_versions("energystock-best-model", stages=["Production"])
    if not versions:
        return "unknown"
    return f"{versions[0].name}_v{versions[0].version}"


def _compute_signal(pred: float) -> str:
    if pred > 0.01:
        return "haussier"
    if pred < -0.01:
        return "baissier"
    return "neutre"


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    df = _load_features(request.ticker, request.as_of_date)

    # Build input vector for model (drop non-feature columns)
    X = df.drop(columns=["date", "ticker", "adj_close", "return"], errors="ignore")
    model = _load_model()
    pred = model.predict(X)[0]

    # Simple intervalle de confiance basé sur +/- 2% de rendement (placeholder)
    interval = [pred - 0.02, pred + 0.02]

    return PredictResponse(
        ticker=request.ticker,
        rendement_predit_5j=float(pred),
        signal=_compute_signal(pred),
        intervalle_confiance=[float(interval[0]), float(interval[1])],
        version_modele=_get_best_model_version(),
        as_of_date=request.as_of_date,
    )

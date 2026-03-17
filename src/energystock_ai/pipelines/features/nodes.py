"""Nodes pour le feature engineering des données financières."""

from __future__ import annotations

import numpy as np
import pandas as pd

from typing import List


def compute_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule les rendements journaliers (pct_change) par ticker."""

    df = df.sort_values(["ticker", "date"]).copy()
    df["return"] = df.groupby("ticker")["adj_close"].pct_change()
    return df


def add_lag_features(
    df: pd.DataFrame, lag_period: int, correlation_threshold: float, target_ticker: str
) -> pd.DataFrame:
    """Ajoute des lags des rendements et filtre selon corrélation avec le ticker cible."""

    df = df.copy()
    # Pivot pour avoir tickers en colonnes
    pivot = df.pivot(index="date", columns="ticker", values="return")
    # Corrélation entre chaque ticker et le target
    corr = pivot.corr()[target_ticker].abs()
    keep_tickers = corr[corr > correlation_threshold].index.tolist()

    # Générer les lags pour chaque ticker retenu
    lagged = pivot[keep_tickers].shift(lag_period)
    lagged.columns = [f"lag_{lag_period}_{t}" for t in lagged.columns]
    lagged = lagged.reset_index()

    df = df.merge(lagged, on="date", how="left")
    return df


def add_technical_indicators(
    df: pd.DataFrame,
    sma_windows: List[int],
    ema_windows: List[int],
    rsi_windows: List[int],
) -> pd.DataFrame:
    """Ajoute SMA, EMA et RSI pour chaque ticker en normalisant par le prix."""

    def rsi(series: pd.Series, window: int) -> pd.Series:
        delta = series.diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        ma_up = up.rolling(window=window, min_periods=1).mean()
        ma_down = down.rolling(window=window, min_periods=1).mean()
        rs = ma_up / (ma_down + 1e-8)
        return 100 - (100 / (1 + rs))

    out = []
    for ticker, group in df.groupby("ticker"):
        group = group.sort_values("date").copy()
        for w in sma_windows:
            group[f"sma_{w}"] = group["adj_close"].rolling(window=w, min_periods=1).mean() / group["adj_close"]
        for w in ema_windows:
            group[f"ema_{w}"] = (
                group["adj_close"].ewm(span=w, adjust=False).mean() / group["adj_close"]
            )
        for w in rsi_windows:
            group[f"rsi_{w}"] = rsi(group["adj_close"], w)
        out.append(group)

    return pd.concat(out, ignore_index=True)


def add_volume_features(df: pd.DataFrame, volume_sma_window: int) -> pd.DataFrame:
    """Ajoute les features de volume (pct_change et moyenne mobile)."""

    df = df.sort_values(["ticker", "date"]).copy()
    df["volume_pct_change"] = df.groupby("ticker")["Volume"].pct_change()
    df["volume_sma"] = (
        df.groupby("ticker")["Volume"].transform(
            lambda x: x.rolling(window=volume_sma_window, min_periods=1).mean()
        )
    )
    return df


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute des variables dummies pour le jour de la semaine."""

    df = df.copy()
    df["weekday"] = df["date"].dt.weekday
    dummies = pd.get_dummies(df["weekday"], prefix="weekday", drop_first=True)
    return pd.concat([df, dummies], axis=1)


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Combine toutes les features et nettoie les NaN."""

    feature_cols = [c for c in df.columns if c not in ["date", "ticker"]]
    return df.dropna(subset=feature_cols).reset_index(drop=True)

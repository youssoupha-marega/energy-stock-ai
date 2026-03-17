"""Tests unitaires pour le pipeline de feature engineering."""

import pandas as pd

from src.energystock_ai.pipelines.features.nodes import (
    add_calendar_features,
    add_lag_features,
    add_technical_indicators,
    add_volume_features,
)


def test_feature_nodes_flow():
    dates = pd.date_range("2020-01-01", periods=6, freq="D")
    df = pd.DataFrame(
        {
            "date": list(dates) * 2,
            "ticker": ["NEE"] * 6 + ["D"] * 6,
            "adj_close": list(range(100, 106)) + list(range(50, 56)),
            "Volume": [1000 + i * 10 for i in range(6)] * 2,
        }
    )
    df["return"] = df.groupby("ticker")["adj_close"].pct_change()

    df = add_lag_features(df, lag_period=1, correlation_threshold=0.0, target_ticker="NEE")
    df = add_technical_indicators(df, sma_windows=[2], ema_windows=[2], rsi_windows=[2])
    df = add_volume_features(df, volume_sma_window=2)
    df = add_calendar_features(df)

    assert "lag_1_NEE" in df.columns
    assert "sma_2" in df.columns
    assert "ema_2" in df.columns
    assert "rsi_2" in df.columns
    assert "volume_pct_change" in df.columns
    assert any(col.startswith("weekday_") for col in df.columns)

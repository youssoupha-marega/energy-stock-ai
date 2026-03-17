"""Tests unitaires pour le pipeline d'ingestion."""

import pandas as pd
import pytest

from src.energystock_ai.pipelines.ingestion.nodes import download_stock_data, filter_missing_tickers


class DummyTicker:
    @staticmethod
    def download(*args, **kwargs):
        # Retourne un DataFrame au format attendu par yfinance
        dates = pd.date_range("2020-01-01", periods=3, freq="D")
        df = pd.DataFrame(
            {
                ("NEE", "Adj Close"): [100, 101, 102],
                ("NEE", "Volume"): [1000, 1100, 1200],
                ("D", "Adj Close"): [50, None, 52],
                ("D", "Volume"): [500, 600, 550],
            },
            index=dates,
        )
        df.columns = pd.MultiIndex.from_tuples(df.columns)
        return df


def test_filter_missing_tickers():
    df = pd.DataFrame(
        {
            "date": ["2020-01-01", "2020-01-02", "2020-01-03"],
            "ticker": ["A", "A", "A"],
            "adj_close": [1.0, None, 3.0],
        }
    )
    filtered = filter_missing_tickers(df, max_missing_pct=0.1)
    assert filtered.empty


def test_download_stock_data_monkeypatch(monkeypatch):
    monkeypatch.setattr("src.energystock_ai.pipelines.ingestion.nodes.yf", DummyTicker)
    df = download_stock_data(["NEE", "D"], start_date="2020-01-01")
    assert "ticker" in df.columns
    assert set(df["ticker"].unique()) == {"NEE", "D"}
    assert "adj_close" in df.columns

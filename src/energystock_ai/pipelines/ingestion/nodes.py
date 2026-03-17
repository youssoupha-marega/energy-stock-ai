"""Nodes pour l'ingestion des données financières depuis Yahoo Finance."""

from __future__ import annotations

import pandas as pd
import yfinance as yf

from datetime import datetime
from typing import List


def download_stock_data(tickers: List[str], start_date: str) -> pd.DataFrame:
    """Télécharge les données ajustées (Adj Close) et le volume de Yahoo Finance.

    Retourne un DataFrame long avec ['date', 'ticker', 'adj_close', 'volume'].
    """

    df = yf.download(
        tickers=tickers,
        start=start_date,
        progress=False,
        group_by="ticker",
        auto_adjust=False,
        threads=True,
    )

    # Si un seul ticker, yfinance renvoie DataFrame 2d, sinon MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        records = []
        for ticker in tickers:
            if ticker not in df.columns.get_level_values(0):
                continue
            ticker_df = df[ticker].copy()
            ticker_df = ticker_df.reset_index()
            ticker_df["ticker"] = ticker
            records.append(ticker_df[["Date", "ticker", "Adj Close", "Volume"]])
        out = pd.concat(records, ignore_index=True)
    else:
        out = df.reset_index()
        out["ticker"] = tickers[0]
        out = out[["Date", "ticker", "Adj Close", "Volume"]]

    out = out.rename(columns={"Date": "date", "Adj Close": "adj_close"})
    out["date"] = pd.to_datetime(out["date"])
    return out


def filter_missing_tickers(df: pd.DataFrame, max_missing_pct: float) -> pd.DataFrame:
    """Supprime les tickers qui ont trop de données manquantes."""

    pct_missing = (
        df.groupby("ticker")["adj_close"].apply(lambda x: x.isna().mean())
    )
    keep = pct_missing[pct_missing <= max_missing_pct].index.tolist()
    return df[df["ticker"].isin(keep)].copy()

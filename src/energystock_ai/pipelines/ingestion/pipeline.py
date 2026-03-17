"""Pipeline Kedro d'ingestion des données via yfinance."""

from kedro.pipeline import Pipeline, node

from .nodes import download_stock_data, filter_missing_tickers


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                func=download_stock_data,
                inputs=["parameters:ingestion.tickers", "parameters:ingestion.start_date"],
                outputs="data_raw",
                name="download_stock_data",
            ),
            node(
                func=filter_missing_tickers,
                inputs=["data_raw", "parameters:ingestion.max_missing_pct"],
                outputs="data_raw",
                name="filter_missing_tickers",
            ),
        ]
    )

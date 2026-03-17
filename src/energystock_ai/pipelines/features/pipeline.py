"""Pipeline Kedro pour le feature engineering."""

from kedro.pipeline import Pipeline, node

from .nodes import (
    add_calendar_features,
    add_lag_features,
    add_technical_indicators,
    add_volume_features,
    build_feature_matrix,
    compute_returns,
)


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                func=compute_returns,
                inputs="data_raw",
                outputs="data_with_returns",
                name="compute_returns",
            ),
            node(
                func=add_lag_features,
                inputs=[
                    "data_with_returns",
                    "parameters:features.lag_period",
                    "parameters:features.correlation_threshold",
                    "parameters:ingestion.target_ticker",
                ],
                outputs="data_with_lags",
                name="add_lag_features",
            ),
            node(
                func=add_technical_indicators,
                inputs=[
                    "data_with_lags",
                    "parameters:features.sma_windows",
                    "parameters:features.ema_windows",
                    "parameters:features.rsi_windows",
                ],
                outputs="data_with_technical",
                name="add_technical_indicators",
            ),
            node(
                func=add_volume_features,
                inputs=["data_with_technical", "parameters:features.volume_sma_window"],
                outputs="data_with_volume",
                name="add_volume_features",
            ),
            node(
                func=add_calendar_features,
                inputs="data_with_volume",
                outputs="data_with_calendar",
                name="add_calendar_features",
            ),
            node(
                func=build_feature_matrix,
                inputs="data_with_calendar",
                outputs="features",
                name="build_feature_matrix",
            ),
        ]
    )

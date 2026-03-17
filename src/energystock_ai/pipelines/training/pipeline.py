"""Pipeline Kedro pour l'entraînement et le suivi MLflow."""

from kedro.pipeline import Pipeline, node

from .nodes import train_and_register


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                func=train_and_register,
                inputs=[
                    "features",
                    "parameters:ingestion.target_ticker",
                    "parameters:training.test_size",
                    "parameters:training.random_state",
                    "parameters:training.mlflow_experiment_name",
                    "parameters:training.random_forest",
                ],
                outputs="training_results",
                name="train_and_register",
            ),
        ]
    )

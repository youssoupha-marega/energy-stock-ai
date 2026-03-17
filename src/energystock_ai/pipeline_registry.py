"""Point d'entrée pour la construction des pipelines Kedro."""

from kedro.pipeline import Pipeline

from energystock_ai.pipelines import (
    create_features_pipeline,
    create_ingestion_pipeline,
    create_training_pipeline,
)


def register_pipelines() -> dict[str, Pipeline]:
    ingestion = create_ingestion_pipeline()
    features = create_features_pipeline()
    training = create_training_pipeline()

    return {
        '__default__': ingestion + features + training,
        'ingestion': ingestion,
        'features': features,
        'training': training,
    }
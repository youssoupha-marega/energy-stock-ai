"""Regroupe les pipelines du projet."""

from energystock_ai.pipelines.features.pipeline import create_pipeline as create_features_pipeline
from energystock_ai.pipelines.ingestion.pipeline import create_pipeline as create_ingestion_pipeline
from energystock_ai.pipelines.training.pipeline import create_pipeline as create_training_pipeline

__all__ = [
    'create_ingestion_pipeline',
    'create_features_pipeline',
    'create_training_pipeline',
]
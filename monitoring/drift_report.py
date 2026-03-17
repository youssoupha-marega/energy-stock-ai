"""Génération de rapports de dérive de données à l'aide d'Evidently AI."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from evidently.dashboard import Dashboard
from evidently.dashboard.tabs import DataDriftTab


def generate_drift_report(
    reference_path: str = "data/02_intermediate/features.parquet",
    current_path: str = "data/02_intermediate/features.parquet",
    output_html: str = "monitoring/drift_report.html",
) -> None:
    """Génère un rapport HTML de dérive entre deux jeux de données."""

    ref = pd.read_parquet(reference_path)
    curr = pd.read_parquet(current_path)

    dashboard = Dashboard(tabs=[DataDriftTab()])
    dashboard.calculate(ref, curr)

    out_path = Path(output_html)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard.save(out_path)


if __name__ == "__main__":
    generate_drift_report()

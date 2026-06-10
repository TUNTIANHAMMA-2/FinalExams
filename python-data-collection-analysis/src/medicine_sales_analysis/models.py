"""Data models returned by the analysis pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class AnalysisResult:
    """Summary of one completed analysis run."""

    output_dir: Path
    raw_rows: int
    cleaned_rows: int
    removed_rows: int
    monthly_average_actual: float


@dataclass(frozen=True)
class CleanedData:
    """Cleaned data plus quality evidence used by reports and tests."""

    raw: pd.DataFrame
    renamed: pd.DataFrame
    cleaned: pd.DataFrame
    removed_rows: pd.DataFrame
    statistical_outliers: pd.DataFrame
    quality_summary: dict[str, Any]


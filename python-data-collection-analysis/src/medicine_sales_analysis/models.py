"""分析流程返回的数据模型。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class AnalysisResult:
    """一次完整分析运行的摘要。"""

    output_dir: Path
    raw_rows: int
    cleaned_rows: int
    removed_rows: int
    monthly_average_actual: float


@dataclass(frozen=True)
class CleanedData:
    """清洗后的数据，以及报告和测试需要的数据质量证据。"""

    raw: pd.DataFrame
    renamed: pd.DataFrame
    cleaned: pd.DataFrame
    removed_rows: pd.DataFrame
    statistical_outliers: pd.DataFrame
    quality_summary: dict[str, Any]

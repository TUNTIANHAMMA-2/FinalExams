"""Exam point 2: inspect basic data information and fix the date column name."""

from __future__ import annotations

from typing import Any

import pandas as pd

from .constants import ORIGINAL_DATE_COLUMN, SALES_TIME_COLUMN


def inspect_raw_data(data: pd.DataFrame) -> dict[str, Any]:
    """Return row count, column metadata, missing counts, and duplicate count."""
    return {
        "row_count": int(len(data)),
        "column_count": int(len(data.columns)),
        "columns": list(data.columns),
        "dtypes": {column: str(dtype) for column, dtype in data.dtypes.items()},
        "missing_counts": {
            column: int(count) for column, count in data.isna().sum().items()
        },
        "duplicate_rows": int(data.duplicated().sum()),
    }


def rename_sales_time(data: pd.DataFrame) -> pd.DataFrame:
    """Rename 购药时间 to 销售时间 as required by the exam brief."""
    renamed = data.rename(columns={ORIGINAL_DATE_COLUMN: SALES_TIME_COLUMN}).copy()
    # Keep the original spreadsheet row number to make anomaly review traceable.
    renamed.insert(0, "源数据行号", renamed.index + 2)
    return renamed


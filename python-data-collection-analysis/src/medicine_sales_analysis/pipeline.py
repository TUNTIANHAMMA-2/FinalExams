"""Orchestrate the medicine sales final-assessment pipeline.

The scoring items live in separate modules so the implementation is easier to
read during defense:

- `data_loading.py` handles data loading.
- `data_overview.py` handles data overview and column rename.
- `data_cleaning.py` handles duplicates, missing values, type conversion,
  anomalies, and time sorting.
- `monthly_sales.py` handles monthly sales and average actual amount.
- `time_actual_relationship.py` handles the sales-time chart data.
- `weekday_sales.py` handles weekday grouping and chart data.
- `top_products.py` handles top-ten product statistics and chart data.
- `outputs.py` persists generated tables, figures, and summaries.
"""

from __future__ import annotations

import logging
from pathlib import Path

from .data_cleaning import clean_sales_data
from .data_loading import load_sales_data
from .data_overview import inspect_raw_data, rename_sales_time
from .models import AnalysisResult, CleanedData
from .monthly_sales import compute_monthly_summary
from .outputs import write_outputs
from .time_actual_relationship import compute_daily_actual
from .top_products import compute_top_products
from .weekday_sales import compute_weekday_summary


LOGGER = logging.getLogger(__name__)


def run_analysis(data_path: Path, output_dir: Path) -> AnalysisResult:
    """Run the complete final-assessment analysis pipeline."""
    LOGGER.info("读取数据：%s", data_path)
    raw_data = load_sales_data(data_path)
    cleaned_data = clean_sales_data(raw_data)
    monthly_summary, monthly_average_actual = compute_monthly_summary(
        cleaned_data.cleaned
    )
    weekday_summary = compute_weekday_summary(cleaned_data.cleaned)
    top_products = compute_top_products(cleaned_data.cleaned)
    daily_actual = compute_daily_actual(cleaned_data.cleaned)

    write_outputs(
        output_dir=output_dir,
        cleaned_data=cleaned_data,
        monthly_summary=monthly_summary,
        monthly_average_actual=monthly_average_actual,
        weekday_summary=weekday_summary,
        top_products=top_products,
        daily_actual=daily_actual,
    )
    return AnalysisResult(
        output_dir=output_dir,
        raw_rows=len(cleaned_data.raw),
        cleaned_rows=len(cleaned_data.cleaned),
        removed_rows=len(cleaned_data.removed_rows),
        monthly_average_actual=monthly_average_actual,
    )


__all__ = [
    "AnalysisResult",
    "CleanedData",
    "clean_sales_data",
    "compute_daily_actual",
    "compute_monthly_summary",
    "compute_top_products",
    "compute_weekday_summary",
    "inspect_raw_data",
    "load_sales_data",
    "rename_sales_time",
    "run_analysis",
]

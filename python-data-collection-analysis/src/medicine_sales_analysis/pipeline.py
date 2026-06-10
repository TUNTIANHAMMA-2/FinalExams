"""调度药品销售期末考查分析流程。

评分点拆分到独立模块中，便于答辩时逐项讲解：

- `data_loading.py` 负责数据加载。
- `data_overview.py` 负责数据概览和列名修正。
- `data_cleaning.py` 负责重复值、缺失值、类型转换、异常值和时间排序。
- `monthly_sales.py` 负责月度销售统计和月均实收金额。
- `time_actual_relationship.py` 负责销售时间关系图的数据。
- `weekday_sales.py` 负责星期分组统计和图表数据。
- `top_products.py` 负责销售数量前十位药品统计和图表数据。
- `outputs.py` 负责保存生成的表格、图表和摘要。
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
    """运行完整期末考查分析流程。"""
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

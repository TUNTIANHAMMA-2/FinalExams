"""Exam point 3: clean duplicates, missing values, types, and anomalies."""

from __future__ import annotations

from typing import Any

import pandas as pd

from .constants import (
    NUMERIC_COLUMNS,
    RENAMED_DATA_COLUMNS,
    SALES_TIME_COLUMN,
    WEEKDAY_NAMES,
)
from .data_overview import inspect_raw_data, rename_sales_time
from .models import CleanedData


def normalize_types(data: pd.DataFrame) -> pd.DataFrame:
    """Convert sales date and numeric fields into analysis-friendly types."""
    normalized = data.copy()
    normalized[SALES_TIME_COLUMN] = pd.to_datetime(
        normalized[SALES_TIME_COLUMN], errors="coerce"
    )
    for column in NUMERIC_COLUMNS:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
    return normalized


def _format_optional_integer(value: Any, missing_label: str) -> str:
    """Format Excel integer-like identifiers without scientific notation."""
    if pd.isna(value):
        return missing_label
    try:
        return str(int(value))
    except (TypeError, ValueError):
        return str(value)


def _join_reasons(row: pd.Series) -> str:
    """Build a human-readable anomaly reason for one row."""
    reasons: list[str] = []
    if pd.isna(row[SALES_TIME_COLUMN]):
        reasons.append("销售时间缺失或日期无效")
    if pd.isna(row["商品名称"]):
        reasons.append("商品名称缺失")
    for column in NUMERIC_COLUMNS:
        if pd.isna(row[column]):
            reasons.append(f"{column}缺失或无法转换为数值")
        elif row[column] <= 0:
            reasons.append(f"{column}小于或等于0")
    return "；".join(reasons)


def _detect_required_field_errors(data: pd.DataFrame) -> pd.Series:
    """Return rows that cannot participate in sales analysis."""
    invalid_date = data[SALES_TIME_COLUMN].isna()
    invalid_product = data["商品名称"].isna()
    invalid_numeric = data[NUMERIC_COLUMNS].isna().any(axis=1)
    non_positive_numeric = (data[NUMERIC_COLUMNS] <= 0).any(axis=1)
    return invalid_date | invalid_product | invalid_numeric | non_positive_numeric


def _detect_statistical_outliers(data: pd.DataFrame) -> pd.DataFrame:
    """Detect IQR outliers after removing rows with definite data errors.

    High sales quantities or amounts can be legitimate bulk purchases, so these
    rows are retained in the cleaned dataset and exported for review instead of
    being blindly deleted.
    """
    outlier_parts: list[pd.DataFrame] = []
    for column in NUMERIC_COLUMNS:
        q1 = data[column].quantile(0.25)
        q3 = data[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        mask = (data[column] < lower_bound) | (data[column] > upper_bound)
        part = data.loc[mask].copy()
        if part.empty:
            continue
        part["异常原因"] = (
            f"{column}超出IQR范围[{lower_bound:.2f}, {upper_bound:.2f}]"
        )
        part["异常字段"] = column
        part["下界"] = lower_bound
        part["上界"] = upper_bound
        outlier_parts.append(part)

    if not outlier_parts:
        return pd.DataFrame()
    return pd.concat(outlier_parts, ignore_index=True)


def clean_sales_data(raw_data: pd.DataFrame) -> CleanedData:
    """Apply all cleaning rules required by the assessment rubric."""
    overview = inspect_raw_data(raw_data)

    # 列名修正：把原始“购药时间”统一为后续分析使用的“销售时间”。
    renamed = rename_sales_time(raw_data)

    # 重复值处理：按业务字段去重，不把“源数据行号”纳入重复判断。
    duplicate_count = int(renamed.duplicated(subset=RENAMED_DATA_COLUMNS).sum())
    deduplicated = renamed.drop_duplicates(subset=RENAMED_DATA_COLUMNS).copy()

    # 类型统一：日期转 DateTime，销售数量/金额转数值，为异常检测做准备。
    normalized = normalize_types(deduplicated)

    # 缺失和确定错误处理：这些行无法参加后续销售统计，直接剔除。
    invalid_mask = _detect_required_field_errors(normalized)
    removed_rows = normalized.loc[invalid_mask].copy()
    if not removed_rows.empty:
        removed_rows["异常原因"] = removed_rows.apply(_join_reasons, axis=1)

    cleaned = normalized.loc[~invalid_mask].copy()
    cleaned["销售数量"] = cleaned["销售数量"].round().astype("int64")
    cleaned["社保卡号"] = cleaned["社保卡号"].map(
        lambda value: _format_optional_integer(value, "未知社保卡")
    )
    cleaned["商品编码"] = cleaned["商品编码"].map(
        lambda value: _format_optional_integer(value, "未知商品编码")
    )

    # 原始“星期”列有错误值；重新从 DateTime 计算，保证星期分组可信。
    cleaned["星期"] = cleaned[SALES_TIME_COLUMN].dt.dayofweek.map(WEEKDAY_NAMES)

    # 评分要求：按照销售时间升序排序并重置索引。
    cleaned = cleaned.sort_values(SALES_TIME_COLUMN).reset_index(drop=True)

    statistical_outliers = _detect_statistical_outliers(cleaned)
    quality_summary = {
        "overview": overview,
        "duplicate_rows_removed": duplicate_count,
        "definite_error_rows_removed": int(len(removed_rows)),
        "statistical_outlier_marks": int(len(statistical_outliers)),
        "cleaned_rows": int(len(cleaned)),
        "date_min": cleaned[SALES_TIME_COLUMN].min().strftime("%Y-%m-%d"),
        "date_max": cleaned[SALES_TIME_COLUMN].max().strftime("%Y-%m-%d"),
        "cleaning_policy": {
            "removed": "缺失关键分析字段、无效日期、销售数量/金额小于等于0的记录",
            "retained_for_review": "IQR统计异常但仍可能是真实大额采购的记录",
        },
    }
    return CleanedData(
        raw=raw_data,
        renamed=renamed,
        cleaned=cleaned,
        removed_rows=removed_rows,
        statistical_outliers=statistical_outliers,
        quality_summary=quality_summary,
    )


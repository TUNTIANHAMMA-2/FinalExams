"""Data pipeline for the medicine sales final assessment.

The assignment is graded around concrete Pandas tasks: load Excel data, inspect
data quality, clean duplicates/missing/anomalous records, compute sales
statistics, and generate charts.  The functions below keep those steps separate
so the code is easy to explain during a short defense.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


LOGGER = logging.getLogger(__name__)

ORIGINAL_DATE_COLUMN = "购药时间"
SALES_TIME_COLUMN = "销售时间"
NUMERIC_COLUMNS = ["销售数量", "应收金额", "实收金额"]
EXPECTED_COLUMNS = [
    ORIGINAL_DATE_COLUMN,
    "社保卡号",
    "商品编码",
    "商品名称",
    "销售数量",
    "应收金额",
    "实收金额",
    "星期",
]
RENAMED_DATA_COLUMNS = [
    SALES_TIME_COLUMN,
    "社保卡号",
    "商品编码",
    "商品名称",
    "销售数量",
    "应收金额",
    "实收金额",
    "星期",
]
REQUIRED_ANALYSIS_COLUMNS = [
    SALES_TIME_COLUMN,
    "商品名称",
    "销售数量",
    "应收金额",
    "实收金额",
]
WEEKDAY_NAMES = {
    0: "星期一",
    1: "星期二",
    2: "星期三",
    3: "星期四",
    4: "星期五",
    5: "星期六",
    6: "星期日",
}
WEEKDAY_ORDER = [WEEKDAY_NAMES[index] for index in range(7)]


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


def load_sales_data(data_path: Path) -> pd.DataFrame:
    """Load the Excel source data and validate that required columns exist."""
    if not data_path.exists():
        raise FileNotFoundError(f"找不到数据文件：{data_path}")

    data = pd.read_excel(data_path)
    missing_columns = [col for col in EXPECTED_COLUMNS if col not in data.columns]
    if missing_columns:
        raise ValueError(f"数据缺少必要列：{', '.join(missing_columns)}")
    return data


def inspect_raw_data(data: pd.DataFrame) -> dict[str, Any]:
    """Return basic information used for the data overview scoring item."""
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


def normalize_types(data: pd.DataFrame) -> pd.DataFrame:
    """Convert dates and numeric fields into analysis-friendly types."""
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
    """Clean raw sales data and collect data-quality evidence."""
    overview = inspect_raw_data(raw_data)
    renamed = rename_sales_time(raw_data)
    duplicate_count = int(renamed.duplicated(subset=RENAMED_DATA_COLUMNS).sum())
    deduplicated = renamed.drop_duplicates(subset=RENAMED_DATA_COLUMNS).copy()
    normalized = normalize_types(deduplicated)

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
    # Recompute weekday from the parsed date so malformed source weekday values
    # such as "2022-02-29" cannot pollute weekday statistics.
    cleaned["星期"] = cleaned[SALES_TIME_COLUMN].dt.dayofweek.map(WEEKDAY_NAMES)
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


def compute_monthly_summary(cleaned: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """Compute monthly sales totals and the average monthly actual amount."""
    working = cleaned.copy()
    working["销售月份"] = working[SALES_TIME_COLUMN].dt.to_period("M").astype(str)
    monthly = (
        working.groupby("销售月份", as_index=False)
        .agg(
            订单数=("商品名称", "count"),
            销售数量合计=("销售数量", "sum"),
            应收金额合计=("应收金额", "sum"),
            实收金额合计=("实收金额", "sum"),
            单笔平均实收金额=("实收金额", "mean"),
        )
        .sort_values("销售月份")
    )
    monthly_average_actual = float(monthly["实收金额合计"].mean())
    return monthly, monthly_average_actual


def compute_weekday_summary(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Group sales by weekday and summarize quantity and amounts."""
    working = cleaned.copy()
    working["星期"] = pd.Categorical(
        working["星期"], categories=WEEKDAY_ORDER, ordered=True
    )
    return (
        working.groupby("星期", observed=False)
        .agg(
            订单数=("商品名称", "count"),
            销售数量合计=("销售数量", "sum"),
            应收金额合计=("应收金额", "sum"),
            实收金额合计=("实收金额", "sum"),
        )
        .reset_index()
    )


def compute_top_products(cleaned: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Return the top products ranked by total sales quantity."""
    return (
        cleaned.groupby("商品名称", as_index=False)
        .agg(
            订单数=("商品名称", "count"),
            销售数量合计=("销售数量", "sum"),
            应收金额合计=("应收金额", "sum"),
            实收金额合计=("实收金额", "sum"),
        )
        .sort_values(["销售数量合计", "实收金额合计"], ascending=[False, False])
        .head(limit)
        .reset_index(drop=True)
    )


def compute_daily_actual(cleaned: pd.DataFrame) -> pd.DataFrame:
    """Aggregate actual payment amount by date for the time-series chart."""
    working = cleaned.copy()
    working["日期"] = working[SALES_TIME_COLUMN].dt.date
    return (
        working.groupby("日期", as_index=False)
        .agg(订单数=("商品名称", "count"), 实收金额合计=("实收金额", "sum"))
        .sort_values("日期")
    )


def configure_plot_style() -> None:
    """Configure Matplotlib/Seaborn for Chinese labels and PNG output."""
    sns.set_theme(style="whitegrid")
    plt.rcParams["font.sans-serif"] = [
        "WenQuanYi Zen Hei",
        "Noto Sans CJK SC",
        "SimHei",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False


def plot_time_vs_actual(daily_actual: pd.DataFrame, output_path: Path) -> None:
    """Plot the relationship between sales date and actual received amount."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(
        pd.to_datetime(daily_actual["日期"]),
        daily_actual["实收金额合计"],
        color="#2563eb",
        linewidth=1.8,
        marker="o",
        markersize=3,
    )
    ax.set_title("销售时间与每日实收金额关系")
    ax.set_xlabel("销售时间")
    ax.set_ylabel("每日实收金额（元）")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_weekday_summary(weekday_summary: pd.DataFrame, output_path: Path) -> None:
    """Plot sales quantity and payment amounts grouped by weekday."""
    fig, ax_quantity = plt.subplots(figsize=(10, 5.5))
    ax_amount = ax_quantity.twinx()

    x_values = range(len(weekday_summary))
    ax_quantity.bar(
        x_values,
        weekday_summary["销售数量合计"],
        width=0.55,
        color="#14b8a6",
        label="销售数量",
    )
    ax_amount.plot(
        x_values,
        weekday_summary["应收金额合计"],
        color="#f97316",
        marker="o",
        linewidth=2,
        label="应收金额",
    )
    ax_amount.plot(
        x_values,
        weekday_summary["实收金额合计"],
        color="#7c3aed",
        marker="s",
        linewidth=2,
        label="实收金额",
    )

    ax_quantity.set_xticks(list(x_values), weekday_summary["星期"])
    ax_quantity.set_ylabel("销售数量")
    ax_amount.set_ylabel("金额（元）")
    ax_quantity.set_title("星期分组下销售数量、应收金额和实收金额")

    handles_1, labels_1 = ax_quantity.get_legend_handles_labels()
    handles_2, labels_2 = ax_amount.get_legend_handles_labels()
    ax_quantity.legend(handles_1 + handles_2, labels_1 + labels_2, loc="upper left")
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def plot_top_products(top_products: pd.DataFrame, output_path: Path) -> None:
    """Plot the top ten medicines by sales quantity."""
    plot_data = top_products.sort_values("销售数量合计", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(plot_data["商品名称"], plot_data["销售数量合计"], color="#0891b2")
    ax.set_title("销售数量前十位药品")
    ax.set_xlabel("销售数量")
    ax.set_ylabel("商品名称")
    for index, value in enumerate(plot_data["销售数量合计"]):
        ax.text(value + 2, index, str(int(value)), va="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def write_markdown_summary(
    output_path: Path,
    cleaned_data: CleanedData,
    monthly_summary: pd.DataFrame,
    monthly_average_actual: float,
    top_products: pd.DataFrame,
) -> None:
    """Write a concise generated Markdown summary for reports and defense."""
    overview = cleaned_data.quality_summary["overview"]
    top_product = top_products.iloc[0]
    lines = [
        "# 药品销售数据分析运行摘要",
        "",
        "## 数据质量",
        "",
        f"- 原始数据：{overview['row_count']} 行，{overview['column_count']} 列。",
        f"- 重复记录：{overview['duplicate_rows']} 行；本次清洗剔除 "
        f"{cleaned_data.quality_summary['duplicate_rows_removed']} 行。",
        f"- 确定错误记录剔除：{len(cleaned_data.removed_rows)} 行。",
        f"- IQR 统计异常标记：{len(cleaned_data.statistical_outliers)} 条，"
        "保留用于业务复核。",
        f"- 清洗后有效数据：{len(cleaned_data.cleaned)} 行。",
        "",
        "## 核心统计",
        "",
        f"- 覆盖日期：{cleaned_data.quality_summary['date_min']} 至 "
        f"{cleaned_data.quality_summary['date_max']}。",
        f"- 月均实收金额：{monthly_average_actual:.2f} 元。",
        f"- 实收金额最高月份："
        f"{monthly_summary.sort_values('实收金额合计', ascending=False).iloc[0]['销售月份']}。",
        f"- 销售数量最高药品：{top_product['商品名称']}，"
        f"销售数量 {int(top_product['销售数量合计'])}。",
        "",
        "## 生成文件",
        "",
        "- `tables/cleaned_medicine_sales.csv`：清洗后的明细数据。",
        "- `tables/monthly_sales_summary.csv`：月度销售统计。",
        "- `tables/weekday_sales_summary.csv`：星期分组统计。",
        "- `tables/top10_products_by_quantity.csv`：销售数量前十药品。",
        "- `tables/anomaly_rows.csv`：剔除和保留复核的异常行。",
        "- `figures/sales_time_actual_amount.png`：销售时间与实收金额关系图。",
        "- `figures/weekday_sales_summary.png`：星期分组统计图。",
        "- `figures/top10_products_by_quantity.png`：销售数量前十药品图。",
        "",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(
    output_dir: Path,
    cleaned_data: CleanedData,
    monthly_summary: pd.DataFrame,
    monthly_average_actual: float,
    weekday_summary: pd.DataFrame,
    top_products: pd.DataFrame,
    daily_actual: pd.DataFrame,
) -> None:
    """Persist cleaned data, summary tables, quality evidence, and charts."""
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    cleaned_data.cleaned.to_csv(
        tables_dir / "cleaned_medicine_sales.csv", index=False, encoding="utf-8-sig"
    )
    monthly_summary.to_csv(
        tables_dir / "monthly_sales_summary.csv", index=False, encoding="utf-8-sig"
    )
    weekday_summary.to_csv(
        tables_dir / "weekday_sales_summary.csv", index=False, encoding="utf-8-sig"
    )
    top_products.to_csv(
        tables_dir / "top10_products_by_quantity.csv",
        index=False,
        encoding="utf-8-sig",
    )

    anomaly_parts = []
    if not cleaned_data.removed_rows.empty:
        removed = cleaned_data.removed_rows.copy()
        removed["处理方式"] = "剔除"
        anomaly_parts.append(removed)
    if not cleaned_data.statistical_outliers.empty:
        retained = cleaned_data.statistical_outliers.copy()
        retained["处理方式"] = "保留复核"
        anomaly_parts.append(retained)
    if anomaly_parts:
        pd.concat(anomaly_parts, ignore_index=True).to_csv(
            tables_dir / "anomaly_rows.csv", index=False, encoding="utf-8-sig"
        )
    else:
        pd.DataFrame(columns=["处理方式", "异常原因"]).to_csv(
            tables_dir / "anomaly_rows.csv", index=False, encoding="utf-8-sig"
        )

    summary = cleaned_data.quality_summary | {
        "monthly_average_actual_amount": monthly_average_actual,
    }
    (tables_dir / "data_quality_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    configure_plot_style()
    plot_time_vs_actual(daily_actual, figures_dir / "sales_time_actual_amount.png")
    plot_weekday_summary(weekday_summary, figures_dir / "weekday_sales_summary.png")
    plot_top_products(top_products, figures_dir / "top10_products_by_quantity.png")

    write_markdown_summary(
        output_path=output_dir / "run-summary.md",
        cleaned_data=cleaned_data,
        monthly_summary=monthly_summary,
        monthly_average_actual=monthly_average_actual,
        top_products=top_products,
    )


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

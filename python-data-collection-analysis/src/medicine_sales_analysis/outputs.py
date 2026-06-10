"""保存清洗数据、统计表、图表和运行摘要。"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .models import CleanedData
from .time_actual_relationship import plot_time_vs_actual
from .top_products import plot_top_products
from .visualization import configure_plot_style
from .weekday_sales import plot_weekday_summary


def write_markdown_summary(
    output_path: Path,
    cleaned_data: CleanedData,
    monthly_summary: pd.DataFrame,
    monthly_average_actual: float,
    top_products: pd.DataFrame,
) -> None:
    """写入用于报告和答辩的简要 Markdown 运行摘要。"""
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
    """保存清洗数据、统计表、数据质量证据和图表。"""
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

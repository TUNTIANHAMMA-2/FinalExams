"""考点：按星期分组汇总销售数据并生成图表。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .constants import WEEKDAY_ORDER
from .visualization import plt


def compute_weekday_summary(cleaned: pd.DataFrame) -> pd.DataFrame:
    """按星期分组统计销售数量和金额。"""
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


def plot_weekday_summary(weekday_summary: pd.DataFrame, output_path: Path) -> None:
    """绘制按星期分组的销售数量和金额图。"""
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

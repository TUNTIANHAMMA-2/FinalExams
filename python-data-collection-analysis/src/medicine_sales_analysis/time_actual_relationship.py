"""考点：分析并绘制销售时间与实收金额的关系。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .constants import SALES_TIME_COLUMN
from .visualization import plt


def compute_daily_actual(cleaned: pd.DataFrame) -> pd.DataFrame:
    """按日期汇总实收金额，用于时间序列图。"""
    working = cleaned.copy()
    working["日期"] = working[SALES_TIME_COLUMN].dt.date
    return (
        working.groupby("日期", as_index=False)
        .agg(订单数=("商品名称", "count"), 实收金额合计=("实收金额", "sum"))
        .sort_values("日期")
    )


def plot_time_vs_actual(daily_actual: pd.DataFrame, output_path: Path) -> None:
    """绘制销售日期与实收金额之间的关系图。"""
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

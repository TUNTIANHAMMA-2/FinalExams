"""Exam point: find and chart the top ten medicines by sales quantity."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .visualization import plt


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

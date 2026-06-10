"""考点：计算月度销售总额和月均实收金额。"""

from __future__ import annotations

import pandas as pd

from .constants import SALES_TIME_COLUMN


def compute_monthly_summary(cleaned: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """计算月度销售汇总和月均实收金额。"""
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

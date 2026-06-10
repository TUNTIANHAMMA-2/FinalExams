"""考点 2：查看数据基本信息并修正日期列名。"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .constants import ORIGINAL_DATE_COLUMN, SALES_TIME_COLUMN


def inspect_raw_data(data: pd.DataFrame) -> dict[str, Any]:
    """返回行列数、字段元数据、缺失值数量和重复行数量。"""
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
    """按照考查要求将“购药时间”改名为“销售时间”。"""
    renamed = data.rename(columns={ORIGINAL_DATE_COLUMN: SALES_TIME_COLUMN}).copy()
    # 保留原始 Excel 行号，方便异常记录回溯。
    renamed.insert(0, "源数据行号", renamed.index + 2)
    return renamed

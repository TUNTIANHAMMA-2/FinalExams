"""考点 1：加载本地药品销售 Excel 数据。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .constants import EXPECTED_COLUMNS


def load_sales_data(data_path: Path) -> pd.DataFrame:
    """读取 Excel 原始数据并校验必要字段。"""
    if not data_path.exists():
        raise FileNotFoundError(f"找不到数据文件：{data_path}")

    data = pd.read_excel(data_path)
    missing_columns = [col for col in EXPECTED_COLUMNS if col not in data.columns]
    if missing_columns:
        raise ValueError(f"数据缺少必要列：{', '.join(missing_columns)}")
    return data

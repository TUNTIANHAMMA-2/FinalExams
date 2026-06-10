"""药品销售分析流程的单元测试。"""

from __future__ import annotations

import unittest

import pandas as pd

from src.medicine_sales_analysis.pipeline import (
    clean_sales_data,
    compute_monthly_summary,
    compute_top_products,
    compute_weekday_summary,
)


class PipelineTest(unittest.TestCase):
    """验证期末考查脚本使用的核心清洗和统计规则。"""

    def setUp(self) -> None:
        self.raw = pd.DataFrame(
            [
                {
                    "购药时间": "2022-01-01",
                    "社保卡号": 1001,
                    "商品编码": 236701,
                    "商品名称": "药品A",
                    "销售数量": 2,
                    "应收金额": 20.0,
                    "实收金额": 18.0,
                    "星期": "星期六",
                },
                {
                    "购药时间": "2022-01-02",
                    "社保卡号": 1002,
                    "商品编码": 236702,
                    "商品名称": "药品B",
                    "销售数量": -1,
                    "应收金额": -10.0,
                    "实收金额": -9.0,
                    "星期": "星期日",
                },
                {
                    "购药时间": "2022-02-29",
                    "社保卡号": 1003,
                    "商品编码": 236703,
                    "商品名称": "药品C",
                    "销售数量": 1,
                    "应收金额": 12.0,
                    "实收金额": 10.0,
                    "星期": "2022-02-29",
                },
                {
                    "购药时间": "2022-02-01",
                    "社保卡号": None,
                    "商品编码": 236701,
                    "商品名称": "药品A",
                    "销售数量": 3,
                    "应收金额": 30.0,
                    "实收金额": 27.0,
                    "星期": "星期二",
                },
            ]
        )

    def test_clean_sales_data_removes_definite_errors(self) -> None:
        cleaned_data = clean_sales_data(self.raw)

        self.assertEqual(len(cleaned_data.cleaned), 2)
        self.assertEqual(len(cleaned_data.removed_rows), 2)
        self.assertIn("销售时间", cleaned_data.cleaned.columns)
        self.assertNotIn("购药时间", cleaned_data.cleaned.columns)
        self.assertEqual(cleaned_data.cleaned["销售数量"].dtype, "int64")
        self.assertEqual(cleaned_data.cleaned.iloc[1]["社保卡号"], "未知社保卡")

    def test_summaries_match_cleaned_sales(self) -> None:
        cleaned = clean_sales_data(self.raw).cleaned
        monthly, monthly_average = compute_monthly_summary(cleaned)
        weekday = compute_weekday_summary(cleaned)
        top_products = compute_top_products(cleaned)

        self.assertEqual(monthly["实收金额合计"].sum(), 45.0)
        self.assertEqual(monthly_average, 22.5)
        self.assertEqual(weekday["销售数量合计"].sum(), 5)
        self.assertEqual(top_products.iloc[0]["商品名称"], "药品A")
        self.assertEqual(top_products.iloc[0]["销售数量合计"], 5)


if __name__ == "__main__":
    unittest.main()

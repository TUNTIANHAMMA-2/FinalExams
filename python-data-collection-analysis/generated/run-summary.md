# 药品销售数据分析运行摘要

## 数据质量

- 原始数据：6578 行，8 列。
- 重复记录：0 行；本次清洗剔除 0 行。
- 确定错误记录剔除：68 行。
- IQR 统计异常标记：2012 条，保留用于业务复核。
- 清洗后有效数据：6510 行。

## 核心统计

- 覆盖日期：2022-01-01 至 2022-07-19。
- 月均实收金额：43434.98 元。
- 实收金额最高月份：2022-01。
- 销售数量最高药品：苯磺酸氨氯地平片(安内真)，销售数量 1781。

## 生成文件

- `tables/cleaned_medicine_sales.csv`：清洗后的明细数据。
- `tables/monthly_sales_summary.csv`：月度销售统计。
- `tables/weekday_sales_summary.csv`：星期分组统计。
- `tables/top10_products_by_quantity.csv`：销售数量前十药品。
- `tables/anomaly_rows.csv`：剔除和保留复核的异常行。
- `figures/sales_time_actual_amount.png`：销售时间与实收金额关系图。
- `figures/weekday_sales_summary.png`：星期分组统计图。
- `figures/top10_products_by_quantity.png`：销售数量前十药品图。

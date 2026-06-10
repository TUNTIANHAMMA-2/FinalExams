# 答辩常见问答

## 1. 为什么把 `购药时间` 改为 `销售时间`？

评分标准明确要求修正列名。`销售时间` 也更贴合后续分析，因为项目关注销售行为，而不是单纯购药记录。

## 2. 为什么不用原始 `星期` 列？

原始 `星期` 列中存在 `2022-02-29` 这样的错误值。代码把销售时间转换为 DateTime 后重新计算星期，可以避免错误源字段污染星期统计。

## 3. 缺失值是怎么处理的？

销售时间、商品名称、销售数量、应收金额和实收金额是分析必需字段，缺失后无法准确统计，因此剔除。社保卡号缺失不影响商品销售统计，因此标记为 `未知社保卡` 后保留。

## 4. 为什么负数销售记录要剔除？

本次分析目标是正常销售表现。销售数量、应收金额、实收金额小于等于 0 的记录无法代表正常销售行为，可能是退货、冲正或录入错误，因此作为确定错误剔除。

## 5. 为什么 IQR 异常不全部删除？

IQR 只能说明数值在统计上偏大或偏小，不能证明数据一定错误。药品销售可能存在真实批量采购，如果直接删除会损失有效业务信息。因此项目把这些记录输出到异常表，保留复核。

## 6. 月均销售金额怎么算？

先按月份汇总每月实收金额，再对各月实收金额求平均。本次月均实收金额为 43434.98 元。

## 7. 哪一天或哪类时间销售最好？

按星期统计后，星期五的订单数、销售数量、应收金额和实收金额都较高，是一周中销售表现最好的日期。

## 8. 销售数量最高的药品是什么？

销售数量最高的是苯磺酸氨氯地平片(安内真)，销售数量为 1781。

## 9. 项目如何保证结果可复核？

程序会输出清洗后的明细、异常记录、月度统计、星期统计、Top 10 统计和 JSON 数据质量摘要。报告中的关键数字都来自这些生成文件。

## 10. 如果老师要求看代码，应该展示哪里？

建议展示：

- `main.py`：一键运行入口。
- `src/medicine_sales_analysis/data_loading.py`：数据加载。
- `src/medicine_sales_analysis/data_overview.py`：数据概览和列名修正。
- `src/medicine_sales_analysis/data_cleaning.py`：核心清洗逻辑。
- `src/medicine_sales_analysis/monthly_sales.py`：月均销售金额。
- `src/medicine_sales_analysis/time_actual_relationship.py`：销售时间与实收金额关系。
- `src/medicine_sales_analysis/weekday_sales.py`：星期分组统计和图表。
- `src/medicine_sales_analysis/top_products.py`：销售数量前十位药品统计和图表。
- `src/medicine_sales_analysis/visualization.py`：图表中文字体和 PNG 输出配置。
- `src/medicine_sales_analysis/pipeline.py`：流程调度。
- `tests/test_pipeline.py`：核心规则测试。

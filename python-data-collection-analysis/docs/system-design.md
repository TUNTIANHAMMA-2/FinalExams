# 系统设计说明

## 1. 总体流程

项目采用单机 Python 数据分析流程：

```text
Excel 原始数据
-> 字段校验
-> 数据概览
-> 列名修正
-> 类型转换
-> 重复/缺失/异常处理
-> 时间排序
-> 月度、星期、商品维度统计
-> CSV/JSON/PNG 输出
-> 报告和答辩引用结果
```

## 2. 技术栈

| 技术 | 用途 |
| --- | --- |
| Python 3.13 | 脚本入口和业务逻辑 |
| Pandas | Excel 读取、清洗、分组统计 |
| NumPy | Pandas 数值计算依赖 |
| Matplotlib | 图表绘制 |
| Seaborn | 图表风格 |
| openpyxl | Excel 读取引擎 |
| unittest | 核心规则测试 |

## 3. 代码模块

| 文件 | 作用 |
| --- | --- |
| `main.py` | 命令行入口，调用完整分析流程 |
| `src/medicine_sales_analysis/pipeline.py` | 数据加载、清洗、统计、绘图和输出 |
| `scripts/build_template_report.py` | 读取原报告模板并生成模板版 Word 报告 |
| `tests/test_pipeline.py` | 验证清洗规则和统计结果 |
| `requirements.txt` | 固定依赖版本 |

## 4. 清洗策略

### 4.1 重复值

在列名修正后，基于销售时间、社保卡号、商品编码、商品名称、销售数量、应收金额、实收金额、星期这些业务字段检测重复。本次数据未发现重复行。

### 4.2 缺失值

关键分析字段缺失会影响统计结果，因此剔除；社保卡号缺失不影响商品销售统计，用 `未知社保卡` 标记保留。

### 4.3 异常值

异常值分两层：

- 确定错误：无效日期、销售数量小于等于 0、应收金额小于等于 0、实收金额小于等于 0。这些记录剔除。
- 统计异常：IQR 检测到的大数量或大金额记录。这些记录可能是批量采购，保留并输出到异常表复核。

## 5. 统计设计

| 统计项 | 输出文件 |
| --- | --- |
| 清洗后明细 | `generated/tables/cleaned_medicine_sales.csv` |
| 月度销售统计 | `generated/tables/monthly_sales_summary.csv` |
| 星期分组统计 | `generated/tables/weekday_sales_summary.csv` |
| Top 10 药品 | `generated/tables/top10_products_by_quantity.csv` |
| 异常记录 | `generated/tables/anomaly_rows.csv` |
| 数据质量摘要 | `generated/tables/data_quality_summary.json` |

## 6. 可视化设计

| 图表 | 作用 |
| --- | --- |
| `sales_time_actual_amount.png` | 展示销售时间与每日实收金额关系 |
| `weekday_sales_summary.png` | 展示每星期销售数量、应收金额和实收金额 |
| `top10_products_by_quantity.png` | 展示销售数量前十位药品 |

图表使用 `WenQuanYi Zen Hei` 等中文字体候选，避免中文标题和坐标轴乱码。

## 7. 报告模板设计

正式提交的 `Python数据收集与分析期末考查报告.docx` 不是普通 Markdown 转 Word，而是基于原始报告模板转换得到的 `.docx` 生成。生成脚本保留模板封面、表格结构和签字栏，把项目名称、项目目的、项目过程、主要结果、图表和个人总结填入模板表格。

## 8. 测试设计

测试覆盖：

- 无效日期和负数销售记录会被剔除。
- `购药时间` 会改名为 `销售时间`。
- 销售数量会转为整型。
- 缺失社保卡号会标记为 `未知社保卡`。
- 月度、星期和 Top 10 统计基于清洗后的数据计算。

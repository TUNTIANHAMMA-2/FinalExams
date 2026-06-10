# 演示流程脚本

本文档用于答辩现场演示，建议控制在 3 到 5 分钟。

## 1. 演示前准备

进入项目目录：

```bash
cd python-data-collection-analysis
```

安装依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. 展示评分标准对应关系

打开 `README.md` 的“评分点对应关系”部分，说明本项目按评分标准逐项实现。

## 3. 运行分析脚本

命令：

```bash
python main.py
```

讲解点：

- 程序自动读取 Excel。
- 自动完成列名修正、类型转换、重复/缺失/异常处理。
- 自动生成统计表、异常表和图表。
- 终端会输出原始行数、清洗后行数、剔除行数和月均实收金额。

## 4. 生成模板版 Word 报告

命令：

```bash
python scripts/build_template_report.py
```

讲解点：

- `Python数据收集与分析期末考查报告.docx` 保留原报告模板的封面、表格框和签字栏。
- `Python数据收集与分析期末考查报告.doc` 由模板版 `.docx` 导出，更贴近原模板文件格式。
- 报告内容和图表来自 `generated/`，避免手工誊写导致数字不一致。

## 5. 展示生成结果

推荐依次打开：

1. `generated/run-summary.md`：总体运行摘要。
2. `generated/tables/data_quality_summary.json`：数据质量证据。
3. `generated/tables/monthly_sales_summary.csv`：月度销售统计。
4. `generated/tables/weekday_sales_summary.csv`：星期分组统计。
5. `generated/tables/top10_products_by_quantity.csv`：销售数量前十药品。

## 6. 展示图表

展示三张图：

- `generated/figures/sales_time_actual_amount.png`
- `generated/figures/weekday_sales_summary.png`
- `generated/figures/top10_products_by_quantity.png`

讲解重点：

- 每日实收金额波动明显。
- 星期五销售表现最好。
- 苯磺酸氨氯地平片(安内真)销售数量最高。

## 7. 展示源码

打开 `src/medicine_sales_analysis/pipeline.py`，重点说明：

- 为什么要先修正列名再处理重复值。
- 为什么要用 DateTime 重新计算星期。
- 为什么对确定错误剔除，对 IQR 大额异常保留复核。
- 函数拆分让代码更容易测试和答辩说明。

## 8. 运行测试

命令：

```bash
python -m unittest discover -s tests
```

讲解点：

测试验证了核心清洗规则和统计规则，不只是“脚本能跑”。

# Python 数据收集与分析期末考查

本目录完成《Python数据收集与分析》期末考查的材料整理、代码实现、分析结果生成和答辩辅助文档。作业主题为药品销售数据处理与分析，核心代码以 `.py` 文件为源头，运行后自动生成清洗数据、统计表和可视化图表。

## 当前状态

| 项目 | 状态 |
| --- | --- |
| 评分标准 / 考查方案 | 已读取并按评分点拆解 |
| 数据加载、概览、列名修正 | 已实现 |
| 重复值、缺失值、异常值处理 | 已实现并输出质量摘要 |
| 排序、月均销售金额、星期分组、Top 10 药品分析 | 已实现 |
| 可视化图表 | 已生成 3 张 PNG |
| 期末报告与答辩文档 | 已补齐，Word 报告已套用原模板格式 |
| 单元测试 | 已通过 |

## 快速运行

建议使用 Python 3.13。

```bash
cd python-data-collection-analysis
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
python scripts/build_template_report.py
python -m unittest discover -s tests
```

运行成功后会在 `generated/` 下生成结果。当前已验证结果：

- 原始数据：6578 行，8 列。
- 清洗后有效数据：6510 行。
- 剔除确定错误记录：68 行。
- 月均实收金额：43434.98 元。
- 销售数量最高药品：苯磺酸氨氯地平片(安内真)，销售数量 1781。

## 目录结构

| 目录 / 文件 | 内容 | 用途 |
| --- | --- | --- |
| `assessment-admin/` | 评分标准、考查方案 | 教师/班级层面的考查说明与评分依据 |
| `student-report-template/` | 期末考查报告模板 | 学生报告格式参考 |
| `exam-materials/data/` | 药品销售数据 Excel | 原始数据 |
| `exam-materials/starter-code/` | 考试题目脚本 | 原始题目骨架 |
| `src/medicine_sales_analysis/` | 清洗、统计、绘图核心逻辑 | 可读、可测试的实现代码 |
| `main.py` | 一键运行入口 | 生成全部结果 |
| `tests/` | 单元测试 | 验证核心清洗和统计规则 |
| `generated/tables/` | CSV/JSON 结果 | 清洗数据、月度统计、星期统计、Top 10、异常记录 |
| `generated/figures/` | PNG 图表 | 报告和答辩用图 |
| `generated/reports/` | PDF 预览 | 由模板版 Word 转出的版式预览 |
| `docs/` | 辅助文档 | 项目理解、系统设计、演示流程、答辩提纲和问答 |
| `Python数据收集与分析期末考查报告.md` | 期末报告内容源 | 便于维护分析正文 |
| `Python数据收集与分析期末考查报告.docx` | 模板版期末报告 | 保留原报告模板封面、表格和签字栏，正式提交优先使用 |
| `Python数据收集与分析期末考查报告.doc` | 旧版 Word 报告 | 由模板版 `.docx` 导出，贴近原模板文件格式 |
| `答辩.md` | 口头汇报稿 | 3 分钟答辩使用 |
| `source-archive/` | 原始 zip 包 | 保留上传原件，避免整理过程丢失来源 |
| `scripts/build_template_report.py` | 模板版报告生成脚本 | 将生成结果填入原报告模板 |

## 评分点对应关系

| 评分点 | 对应实现 |
| --- | --- |
| 数据加载 | `load_sales_data()` 使用 `pandas.read_excel()` 读取 Excel |
| 数据概览 | `inspect_raw_data()` 输出行列数、字段、类型、缺失、重复 |
| 修正列名 | `rename_sales_time()` 将 `购药时间` 改为 `销售时间` |
| 重复值处理 | 基于业务字段检测并删除重复行 |
| 缺失值处理 | 缺失关键分析字段的行剔除；缺失社保卡号用 `未知社保卡` 标记 |
| 异常值处理 | 无效日期、非正销售数量/金额剔除；IQR 统计异常保留复核 |
| 时间排序 | 清洗后按 `销售时间` 升序排序并重置索引 |
| 月均销售金额 | `monthly_sales_summary.csv` 和运行摘要输出月均实收金额 |
| 销售时间与实收金额关系 | `generated/figures/sales_time_actual_amount.png` |
| 星期分组统计 | `weekday_sales_summary.csv` 和对应图表 |
| Top 10 药品 | `top10_products_by_quantity.csv` 和对应图表 |
| 项目汇报 | `答辩.md`、`docs/defense-outline.md`、`docs/defense-qa.md` |

## 文档与代码推进方式

本作业采用“代码先产出证据，文档再引用证据”的交叉方式：先按评分点实现数据处理脚本，生成可复核的 CSV、JSON 和 PNG；随后报告、答辩稿和辅助文档直接引用这些输出，避免文档结论和实际运行结果不一致。

正式 Word 报告由 `scripts/build_template_report.py` 生成，脚本读取原模板转换得到的 `student-report-template/期末考查报告模板（学生一人一份，不打印）.docx`，保留封面、表格框和签字栏，再填入本次分析内容与图表。根目录同时提供 `.docx` 和由 LibreOffice 导出的 `.doc`，正式提交可优先使用 `.doc`。

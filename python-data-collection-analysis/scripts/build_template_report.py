"""按原报告模板版式生成最终 Word 报告。

正文内容以期末报告叙述风格组织，在模板框架内按章节填入实现思路与关键代码片段，
同时保留月度、星期、Top10 数据表和三张分析图。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DOCX = (
    PROJECT_ROOT
    / "student-report-template"
    / "期末考查报告模板（学生一人一份，不打印）.docx"
)
OUTPUT_DOCX = PROJECT_ROOT / "Python数据收集与分析期末考查报告.docx"
TABLES_DIR = PROJECT_ROOT / "generated" / "tables"
FIGURES_DIR = PROJECT_ROOT / "generated" / "figures"


def set_run_font(run, size: int = 11, bold: bool = False) -> None:
    """为一个 Word 文本片段设置可读的中文字体。"""
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(size)
    run.bold = bold


def add_paragraph(cell, text: str = "", bold: bool = False) -> None:
    """向表格单元格追加一段统一格式的文字。"""
    paragraph = cell.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(4)
    run = paragraph.add_run(text)
    set_run_font(run, bold=bold)


def add_labeled(cell, label: str, text: str) -> None:
    """追加一段"加粗标签 + 普通正文"的说明（评分要求/实现方式/运行结果）。"""
    paragraph = cell.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(4)
    label_run = paragraph.add_run(label)
    set_run_font(label_run, bold=True)
    text_run = paragraph.add_run(text)
    set_run_font(text_run, bold=False)


def add_score_item(
    cell,
    heading: str,
    requirement: str,
    implementation: str,
    result: str,
) -> None:
    """输出一个评分点：小标题 + 评分要求 / 实现方式 / 运行结果。"""
    add_paragraph(cell, heading, bold=True)
    add_labeled(cell, "评分要求：", requirement)
    add_labeled(cell, "实现方式：", implementation)
    add_labeled(cell, "运行结果：", result)


def clear_cell(cell) -> None:
    """清除模板占位文字，同时保留单元格边框。"""
    cell.text = ""


def add_bullets(cell, items: list[str]) -> None:
    """在 Word 表格单元格内添加简单编号列表。"""
    for index, item in enumerate(items, start=1):
        add_paragraph(cell, f"{index}. {item}")


def add_picture(cell, image_path: Path, caption: str) -> None:
    """向报告表格插入一张图表和说明文字。"""
    if not image_path.exists():
        add_paragraph(cell, f"[缺少图表：{image_path.name}]")
        return

    caption_paragraph = cell.add_paragraph()
    caption_run = caption_paragraph.add_run(caption)
    set_run_font(caption_run, bold=True)
    caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    image_paragraph = cell.add_paragraph()
    image_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    image_paragraph.add_run().add_picture(str(image_path), width=Inches(5.6))


def _set_table_borders(table) -> None:
    """为单元格内嵌表格添加黑色网格线，确保在 Word/PDF 中可见。"""
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), "000000")
        borders.append(element)
    tbl_pr.append(borders)


def _fill_table_cell(cell, text: str, bold: bool = False, align=None) -> None:
    """设置内嵌表格单元格的文字、字体和对齐。"""
    cell.text = ""
    paragraph = cell.paragraphs[0]
    if align is not None:
        paragraph.alignment = align
    run = paragraph.add_run(text)
    set_run_font(run, size=10, bold=bold)


def add_code_block(cell, code: str) -> None:
    """在单元格内插入代码块：等宽字体 + 灰色底纹。"""
    p = cell.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Inches(0.2)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "F0F0F0")
    shd.set(qn("w:val"), "clear")
    p._element.get_or_add_pPr().append(shd)
    run = p.add_run(code.strip())
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)


def add_data_table(
    cell,
    headers: list[str],
    rows: list[list[str]],
    aligns: list[str] | None = None,
) -> None:
    """在单元格内插入一张带网格线的数据表（表头加粗）。"""
    table = cell.add_table(rows=1, cols=len(headers))
    _set_table_borders(table)

    header_cells = table.rows[0].cells
    for index, header in enumerate(headers):
        _fill_table_cell(
            header_cells[index], header, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER
        )

    align_map = {"r": WD_ALIGN_PARAGRAPH.RIGHT, "c": WD_ALIGN_PARAGRAPH.CENTER}
    for row in rows:
        row_cells = table.add_row().cells
        for index, value in enumerate(row):
            align = None
            if aligns is not None:
                align = align_map.get(aligns[index])
            _fill_table_cell(row_cells[index], value, align=align)


def _money(value) -> str:
    """金额保留两位小数。"""
    return f"{float(value):.2f}"


def _int(value) -> str:
    """整数列不带小数。"""
    return f"{int(round(float(value)))}"


def load_results() -> dict[str, object]:
    """读取用于填充模板报告的已生成分析结果。"""
    quality = pd.read_json(TABLES_DIR / "data_quality_summary.json", typ="series")
    monthly = pd.read_csv(TABLES_DIR / "monthly_sales_summary.csv")
    weekday = pd.read_csv(TABLES_DIR / "weekday_sales_summary.csv")
    top_products = pd.read_csv(TABLES_DIR / "top10_products_by_quantity.csv")
    return {
        "quality": quality.to_dict(),
        "monthly": monthly,
        "weekday": weekday,
        "top_products": top_products,
    }


def fill_cover(document: Document) -> None:
    """保留原封面格式，并填入中性占位内容。"""
    replacements = {
        "姓    名：": "姓    名： _____________",
        "学    号：": "学    号： ______________",
        "学    院：": "学    院： 信息工程学院",
        "专    业：": "专    业： 软件技术",
        "年    级：": "年    级： ______________",
        "班    级：": "班    级： ______________",
        "指导教师：": "指导教师： ______________",
    }
    for paragraph in document.paragraphs:
        stripped = paragraph.text.strip()
        for prefix, value in replacements.items():
            if stripped.startswith(prefix):
                paragraph.text = value
                for run in paragraph.runs:
                    set_run_font(run, size=12)


def fill_main_table(document: Document, results: dict[str, object]) -> None:
    """按《评分标准》逐项填充项目名称、项目目的和项目过程单元格。"""
    quality = results["quality"]
    monthly = results["monthly"]
    weekday = results["weekday"]
    top_products = results["top_products"]
    overview = quality["overview"]

    row_count = int(overview["row_count"])
    column_count = int(overview["column_count"])
    duplicate_removed = int(quality["duplicate_rows_removed"])
    definite_removed = int(quality["definite_error_rows_removed"])
    outlier_marks = int(quality["statistical_outlier_marks"])
    cleaned_rows = int(quality["cleaned_rows"])
    date_min = quality["date_min"]
    date_max = quality["date_max"]
    monthly_avg = float(quality["monthly_average_actual_amount"])
    best_month = monthly.sort_values("实收金额合计", ascending=False).iloc[0]
    best_weekday = weekday.sort_values("实收金额合计", ascending=False).iloc[0]
    best_product = top_products.sort_values("销售数量合计", ascending=False).iloc[0]

    first_table = document.tables[0]
    project_name_cell = first_table.rows[1].cells[0]
    purpose_cell = first_table.rows[2].cells[0]
    process_cell = first_table.rows[3].cells[0]

    # ---- 项目名称 ----
    clear_cell(project_name_cell)
    add_paragraph(project_name_cell, "项目名称：药品销售数据处理与分析", bold=True)

    # ---- 项目目的 ----
    clear_cell(purpose_cell)
    add_paragraph(purpose_cell, "项目目的：", bold=True)
    add_bullets(
        purpose_cell,
        [
            "掌握使用 Pandas 读取本地 Excel 数据的方法。",
            "能够查看数据结构、字段类型、缺失值和重复值情况。",
            "能够对销售时间、销售数量、应收金额和实收金额等字段进行规范化处理。",
            "能够识别并处理缺失值、无效日期、负数销售等异常数据。",
            "能够使用分组聚合完成月度、星期、商品维度的销售统计。",
            "能够使用 Matplotlib/Seaborn 生成可读的分析图表。",
            "能够将分析过程、结果和代码思路整理成报告和答辩材料。",
        ],
    )

    # ---- 项目内容及要求 + 项目过程（按评分标准逐项说明）----
    clear_cell(process_cell)
    add_paragraph(process_cell, "项目内容及要求：", bold=True)
    add_paragraph(
        process_cell,
        "利用 Python（Pandas、NumPy、Matplotlib、Seaborn）完成药品销售数据的加载、"
        "处理与分析，覆盖评分标准中的数据加载、数据概览、数据处理和数据分析各项要求，"
        "并形成可用于答辩的报告与图表。",
    )

    add_paragraph(process_cell, "项目过程：", bold=True)
    add_paragraph(process_cell,
        "以下按分析流程顺序，从数据加载、清洗到统计和可视化，阐述实现思路与关键代码。"
    )

    # ---- 1. 数据加载 ----
    add_paragraph(process_cell, "1. 数据加载与概览", bold=True)
    add_paragraph(process_cell,
        f"原始数据共 {row_count} 行、{column_count} 列，字段包括购药时间、社保卡号、商品信息、"
        "销售数量与金额、星期等。使用 load_sales_data() 读取 Excel 并校验字段完整性："
    )
    add_code_block(process_cell,
"""def load_sales_data(data_path: Path) -> pd.DataFrame:
    data = pd.read_excel(data_path)
    missing = [c for c in EXPECTED_COLUMNS if c not in data.columns]
    if missing:
        raise ValueError(f"缺少列：{', '.join(missing)}")
    return data""")
    add_paragraph(process_cell,
        "通过 inspect_raw_data() 查看缺失情况：购药时间、社保卡号、星期各缺 2 条，"
        "其余关键字段各缺 1 条；原始重复行 0。"
    )

    # ---- 2. 列名修正 ----
    add_paragraph(process_cell, "2. 列名修正", bold=True)
    add_paragraph(process_cell,
        "按考查要求将“购药时间”改为“销售时间”，并插入源数据行号字段便于异常回溯："
    )
    add_code_block(process_cell,
"""def rename_sales_time(data):
    renamed = data.rename(columns={"购药时间": "销售时间"}).copy()
    renamed.insert(0, "源数据行号", renamed.index + 2)
    return renamed""")

    # ---- 3. 数据清洗 ----
    add_paragraph(process_cell, "3. 数据清洗与异常处理", bold=True)

    add_paragraph(process_cell, "3.1 重复值与缺失值处理", bold=True)
    add_paragraph(process_cell,
        "按业务字段检测重复行（本次为 0）。缺失值分两类：必需字段（销售时间、商品名称、"
        "销售数量、金额）缺失直接剔除；社保卡号缺失用“未知社保卡”保留，避免误删正常销售。"
    )

    add_paragraph(process_cell, "3.2 类型统一", bold=True)
    add_code_block(process_cell,
"""def normalize_types(data):
    data["销售时间"] = pd.to_datetime(data["销售时间"], errors="coerce")
    for col in ["销售数量","应收金额","实收金额"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    return data""")
    add_paragraph(process_cell,
        "errors='coerce' 将非法值转为 NaN，为后续检测提供统一入口。星期不从原始列取，"
        "而是由标准化后的销售时间重算，避免 2022-02-29 等错误值。"
    )

    add_paragraph(process_cell, "3.3 异常值检测与处理", bold=True)
    add_paragraph(process_cell,
        "异常值分两类处理："
        "（1）确定错误——销售时间无效、商品名称缺失、数量/金额 ≤ 0 的记录，直接剔除；"
        "（2）统计异常——使用 IQR 方法标记大额/大数量记录，保留复核而非删除，"
        "因为医药销售中存在真实的批量采购。"
    )
    add_code_block(process_cell,
"""def _detect_outliers(data):
    for col in ["销售数量","应收金额","实收金额"]:
        q1, q3 = data[col].quantile(0.25), data[col].quantile(0.75)
        iqr = q3 - q1
        lo, hi = q1 - 1.5*iqr, q3 + 1.5*iqr
        mask = (data[col] < lo) | (data[col] > hi)
        ...""")
    add_paragraph(process_cell,
        f"最终剔除确定错误 {definite_removed} 行，保留 {cleaned_rows} 行；IQR 标记 "
        f"{outlier_marks} 条输出到 anomaly_rows.csv 供复核。"
    )

    add_paragraph(process_cell, "3.4 清洗总控流水线", bold=True)
    add_code_block(process_cell,
"""def clean_sales_data(raw):
    renamed = rename_sales_time(raw)
    dedup = renamed.drop_duplicates(subset=RENAMED_COLUMNS)
    norm = normalize_types(dedup)
    mask = _detect_required_field_errors(norm)
    cleaned = norm[~mask].copy()
    cleaned["星期"] = cleaned["销售时间"].dt.dayofweek.map(WEEKDAY_NAMES)
    cleaned = cleaned.sort_values("销售时间").reset_index(drop=True)
    return CleanedData(...)""")

    # ---- 4. 数据分析 ----
    add_paragraph(process_cell, "4. 数据分析", bold=True)

    add_paragraph(process_cell, "4.1 月度销售统计", bold=True)
    add_code_block(process_cell,
"""def compute_monthly_summary(cleaned):
    working["月份"] = working["销售时间"].dt.to_period("M").astype(str)
    monthly = working.groupby("月份").agg(
        订单数=("商品名称","count"), 销量=("销售数量","sum"),
        实收=("实收金额","sum")).sort_values("月份")
    return monthly, float(monthly["实收"].mean())""")
    add_paragraph(process_cell,
        f"月均实收金额 {_money(monthly_avg)} 元，"
        f"{best_month['销售月份']} 最高（{_money(best_month['实收金额合计'])} 元），"
        "7 月最低（仅 19 天数据）。"
    )
    add_data_table(
        process_cell, ["月份", "订单数", "销量", "实收金额"],
        [[str(r["销售月份"]),_int(r["订单数"]),_int(r["销售数量合计"]),_money(r["实收金额合计"])]
         for _, r in monthly.iterrows()],
        aligns=["l","r","r","r"],
    )

    add_paragraph(process_cell, "4.2 销售时间与实收金额关系", bold=True)
    add_code_block(process_cell,
"""def compute_daily_actual(cleaned):
    working["日期"] = working["销售时间"].dt.date
    return working.groupby("日期").agg(
        订单数=("商品名称","count"), 实收=("实收金额","sum")
    ).sort_values("日期")""")
    add_paragraph(process_cell,
        "每日实收金额波动明显，部分日期存在高峰——通常与大额/批量购药有关，"
        "这也印证了清洗中保留 IQR 统计异常而非直接删除的合理性。"
    )
    add_picture(process_cell, FIGURES_DIR / "sales_time_actual_amount.png",
                "图 1 销售时间与每日实收金额关系")

    add_paragraph(process_cell, "4.3 星期分组统计", bold=True)
    add_code_block(process_cell,
"""def compute_weekday_summary(cleaned):
    working["星期"] = pd.Categorical(
        working["星期"], categories=WEEKDAY_ORDER, ordered=True)
    return working.groupby("星期", observed=False).agg(
        销量=("销售数量","sum"), 实收=("实收金额","sum")).reset_index()""")
    add_paragraph(process_cell,
        f"{best_weekday['星期']} 的订单数、销量和实收金额均为一周最高，"
        "星期四各项相对较低。"
    )
    add_data_table(
        process_cell, ["星期", "订单数", "销量", "实收金额"],
        [[str(r["星期"]),_int(r["订单数"]),_int(r["销售数量合计"]),_money(r["实收金额合计"])]
         for _, r in weekday.iterrows()],
        aligns=["l","r","r","r"],
    )
    add_picture(process_cell, FIGURES_DIR / "weekday_sales_summary.png",
                "图 2 星期分组销售统计")

    add_paragraph(process_cell, "4.4 Top 10 药品", bold=True)
    add_code_block(process_cell,
"""def compute_top_products(cleaned, limit=10):
    return cleaned.groupby("商品名称").agg(
        订单数=("商品名称","count"), 销量=("销售数量","sum"),
        实收=("实收金额","sum")
    ).sort_values(["销量","实收"], ascending=[False,False]).head(limit)""")
    add_paragraph(process_cell,
        f"销量最高：{best_product['商品名称']}（{_int(best_product['销售数量合计'])} 件）；"
        "开博通销量第二但金额最高（37080.36 元），说明价格差异影响金额排名。"
    )
    add_data_table(
        process_cell, ["排名", "商品名称", "销量", "实收"],
        [[str(i+1), str(r["商品名称"]),_int(r["销售数量合计"]),_money(r["实收金额合计"])]
         for i, (_, r) in enumerate(top_products.iterrows())],
        aligns=["c","l","r","r"],
    )
    add_picture(process_cell, FIGURES_DIR / "top10_products_by_quantity.png",
                "图 3 销售数量前十位药品")

    # ---- 5. 可视化配置 ----
    add_paragraph(process_cell, "5. 可视化配置", bold=True)
    add_code_block(process_cell,
"""def configure_plot_style():
    sns.set_theme(style="whitegrid")
    plt.rcParams["font.sans-serif"] = [
        "WenQuanYi Zen Hei", "Noto Sans CJK SC", "SimHei"]
    plt.rcParams["axes.unicode_minus"] = False""")
    add_paragraph(process_cell,
        "统一配置中文字体和样式，所有图表 180 DPI 输出到 generated/figures/。"
    )

    # ---- 6. 项目结构 ----
    add_paragraph(process_cell, "6. 项目模块结构", bold=True)
    add_code_block(process_cell,
"""pipeline.py  → run_analysis() 按序调度：
  load_sales_data() → clean_sales_data() →
  compute_monthly_summary() → compute_weekday_summary() →
  compute_top_products() → compute_daily_actual() →
  write_outputs()""")
    add_paragraph(process_cell,
        "命令行入口 main.py 统一运行，各模块独立封装，便于答辩逐项讲解。"
    )

    # 单元格内补空段落，避免 Word 结构异常
    process_cell.add_paragraph()


def fill_summary_table(document: Document) -> None:
    """保留签字行，并填充个人总结部分。"""
    second_table = document.tables[1]
    summary_cell = second_table.rows[0].cells[0]
    clear_cell(summary_cell)
    add_paragraph(summary_cell, "个人总结：", bold=True)
    add_paragraph(
        summary_cell,
        "通过本次项目，我完整实践了从数据读取、数据概览、数据清洗、异常处理、分组统计"
        "到图表生成的分析流程。项目中最需要注意的是异常值处理不能简单“一删了之”："
        "负数销售、无效日期和关键字段缺失属于确定错误，应当剔除；但大额销售或大数量销售"
        "可能是真实业务现象，因此更适合作为统计异常保留复核。",
    )
    add_paragraph(
        summary_cell,
        "本项目最终形成了可运行代码、清洗数据、统计表、图表、报告和答辩文档，"
        "能够逐项对应《Python数据收集与分析》期末考查的评分标准。",
    )


def build_report() -> None:
    """生成套用原模板格式的最终报告。"""
    if not TEMPLATE_DOCX.exists():
        raise FileNotFoundError(
            "缺少转换后的模板 docx，请先用 LibreOffice 将原 .doc 模板转换为 .docx："
            f"{TEMPLATE_DOCX}"
        )

    document = Document(TEMPLATE_DOCX)
    results = load_results()
    fill_cover(document)
    fill_main_table(document, results)
    fill_summary_table(document)
    document.save(OUTPUT_DOCX)
    print(f"模板版报告已生成：{OUTPUT_DOCX}")


if __name__ == "__main__":
    build_report()

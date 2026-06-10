"""按原报告模板版式生成最终 Word 报告。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


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


def format_top_products(top_products: pd.DataFrame, limit: int = 5) -> list[str]:
    """返回前几名药品排行的简短文本。"""
    lines: list[str] = []
    for index, row in top_products.head(limit).iterrows():
        lines.append(
            f"{index + 1}. {row['商品名称']}：销售数量"
            f"{int(row['销售数量合计'])}，实收金额{row['实收金额合计']:.2f}元。"
        )
    return lines


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
    """填充模板中的项目目的和项目过程单元格。"""
    quality = results["quality"]
    monthly = results["monthly"]
    weekday = results["weekday"]
    top_products = results["top_products"]

    first_table = document.tables[0]
    project_name_cell = first_table.rows[1].cells[0]
    purpose_cell = first_table.rows[2].cells[0]
    process_cell = first_table.rows[3].cells[0]

    clear_cell(project_name_cell)
    add_paragraph(project_name_cell, "项目名称：药品销售数据处理与分析", bold=True)

    clear_cell(purpose_cell)
    add_paragraph(purpose_cell, "项目目的：", bold=True)
    add_bullets(
        purpose_cell,
        [
            "掌握使用 Pandas 读取本地 Excel 数据的方法。",
            "能够查看数据字段、类型、缺失值和重复值情况。",
            "能够完成销售时间、销售数量和金额字段的规范化处理。",
            "能够识别并处理缺失值、无效日期和非正常销售数据。",
            "能够按月份、星期和商品名称完成销售统计分析。",
            "能够使用 Matplotlib/Seaborn 生成可读的数据可视化图表。",
        ],
    )

    clear_cell(process_cell)
    add_paragraph(process_cell, "项目内容及要求：", bold=True)
    add_paragraph(
        process_cell,
        "本项目使用 Python 对药品销售数据进行加载、清洗、统计和可视化，"
        "覆盖评分标准中的数据加载、数据概览、列名修正、重复值处理、"
        "缺失值处理、异常值处理、月均销售金额、星期分组统计和销售数量"
        "前十位药品分析。",
    )

    add_paragraph(process_cell, "项目过程：", bold=True)
    add_bullets(
        process_cell,
        [
            "读取原始 Excel，原始数据共 6578 行、8 列。",
            "将“购药时间”修正为“销售时间”，并转换为 DateTime 类型。",
            "销售数量转换为整型，应收金额和实收金额转换为数值类型。",
            "剔除无效日期、关键字段缺失、销售数量或金额小于等于 0 的记录，共 68 行。",
            "清洗后保留 6510 行有效数据，并按销售时间升序排序、重置索引。",
            "按月份计算销售统计，月均实收金额为 43434.98 元。",
            "按星期统计销售数量、应收金额和实收金额，星期五销售表现最好。",
            "按商品名称统计销售数量，苯磺酸氨氯地平片(安内真)排名第一。",
        ],
    )

    best_month = monthly.sort_values("实收金额合计", ascending=False).iloc[0]
    best_weekday = weekday.sort_values("实收金额合计", ascending=False).iloc[0]
    add_paragraph(process_cell, "主要结果：", bold=True)
    add_paragraph(
        process_cell,
        f"数据覆盖日期为{quality['date_min']}至{quality['date_max']}；"
        f"实收金额最高月份为{best_month['销售月份']}，金额"
        f"{best_month['实收金额合计']:.2f}元；实收金额最高星期为"
        f"{best_weekday['星期']}，金额{best_weekday['实收金额合计']:.2f}元。",
    )
    for line in format_top_products(top_products):
        add_paragraph(process_cell, line)

    add_picture(
        process_cell,
        FIGURES_DIR / "sales_time_actual_amount.png",
        "图 1 销售时间与每日实收金额关系",
    )
    add_picture(
        process_cell,
        FIGURES_DIR / "weekday_sales_summary.png",
        "图 2 星期分组销售统计",
    )
    add_picture(
        process_cell,
        FIGURES_DIR / "top10_products_by_quantity.png",
        "图 3 销售数量前十位药品",
    )


def fill_summary_table(document: Document) -> None:
    """保留签字行，并填充个人总结部分。"""
    second_table = document.tables[1]
    summary_cell = second_table.rows[0].cells[0]
    clear_cell(summary_cell)
    add_paragraph(summary_cell, "个人总结：", bold=True)
    add_paragraph(
        summary_cell,
        "本次项目完整实践了 Python 数据分析流程：从 Excel 数据加载开始，"
        "依次完成数据概览、列名修正、类型转换、重复值处理、缺失值处理、"
        "异常值处理、分组统计和可视化。项目中最关键的是异常值处理策略："
        "无效日期、非正销售数量和金额属于确定错误，应当剔除；而 IQR "
        "检测到的大额或大数量记录可能是真实批量采购，因此保留并输出异常表复核。",
    )
    add_paragraph(
        summary_cell,
        "通过本项目，我进一步理解了数据清洗不是机械删除数据，而是要结合业务含义"
        "说明处理依据。最终代码、统计表、图表、报告和答辩材料保持一致，"
        "能够较完整地对应本课程期末考查评分标准。",
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

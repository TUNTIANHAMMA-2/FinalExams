"""Command line entrypoint for the medicine sales data analysis assignment."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from src.medicine_sales_analysis.pipeline import run_analysis


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = PROJECT_ROOT / "exam-materials" / "data" / "药品销售数据.xlsx"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "generated"


def build_parser() -> argparse.ArgumentParser:
    """Create the command line parser used by the assignment script."""
    parser = argparse.ArgumentParser(
        description="完成《Python数据收集与分析》药品销售数据清洗、统计和可视化。"
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help="Excel 数据文件路径，默认使用 exam-materials/data/药品销售数据.xlsx。",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="分析结果输出目录，默认写入 generated/。",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示调试日志。",
    )
    return parser


def main() -> int:
    """Run the full analysis pipeline and print a compact result summary."""
    args = build_parser().parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    result = run_analysis(data_path=args.data, output_dir=args.output)
    summary_path = result.output_dir / "tables" / "data_quality_summary.json"

    print("药品销售数据分析完成")
    print(f"- 原始数据行数：{result.raw_rows}")
    print(f"- 清洗后行数：{result.cleaned_rows}")
    print(f"- 剔除确定错误行数：{result.removed_rows}")
    print(f"- 月均实收金额：{result.monthly_average_actual:.2f} 元")
    print(f"- 输出目录：{result.output_dir}")
    print(f"- 质量摘要：{summary_path}")

    # Keep a machine-readable one-line summary for shell users and graders.
    print(
        json.dumps(
            {
                "raw_rows": result.raw_rows,
                "cleaned_rows": result.cleaned_rows,
                "removed_rows": result.removed_rows,
                "monthly_average_actual": round(result.monthly_average_actual, 2),
                "output_dir": str(result.output_dir),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


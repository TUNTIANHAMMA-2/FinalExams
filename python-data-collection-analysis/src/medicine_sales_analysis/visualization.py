"""药品销售考查图表的共享绘图配置。"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns


def configure_plot_style() -> None:
    """配置 Matplotlib/Seaborn，使其支持中文标签和 PNG 输出。"""
    sns.set_theme(style="whitegrid")
    plt.rcParams["font.sans-serif"] = [
        "WenQuanYi Zen Hei",
        "Noto Sans CJK SC",
        "SimHei",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False

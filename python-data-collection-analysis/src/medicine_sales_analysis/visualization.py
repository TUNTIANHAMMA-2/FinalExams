"""Shared plotting setup for the medicine sales assessment charts."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns


def configure_plot_style() -> None:
    """Configure Matplotlib/Seaborn for Chinese labels and PNG output."""
    sns.set_theme(style="whitegrid")
    plt.rcParams["font.sans-serif"] = [
        "WenQuanYi Zen Hei",
        "Noto Sans CJK SC",
        "SimHei",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False

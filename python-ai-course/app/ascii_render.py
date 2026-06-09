from __future__ import annotations

import numpy as np

from app import preprocess


def frame_to_ascii(frame, width: int, charset: str) -> str:
    """把摄像头画面灰度值映射为字符，生成命令行实时预览内容。"""
    gray = preprocess.to_ascii_gray(frame, width)
    indices = np.floor(gray / 256 * len(charset)).astype(int)
    indices = np.clip(indices, 0, len(charset) - 1)
    lines = []
    for row in indices:
        lines.append("".join(charset[index] for index in row))
    return "\n".join(lines)

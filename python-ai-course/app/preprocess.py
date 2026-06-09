from __future__ import annotations

import cv2


def prepare_frame(frame, scale: float):
    """将摄像头原始帧缩放、灰度化并均衡化，作为人脸检测和识别的输入。"""
    small = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    return cv2.equalizeHist(gray)


def to_ascii_gray(frame, width: int):
    """按指定宽度压缩画面并转成灰度矩阵，供 ASCII 预览渲染使用。"""
    height, original_width = frame.shape[:2]
    ratio = height / max(original_width, 1)
    resized_height = max(1, int(width * ratio * 0.55))
    resized = cv2.resize(frame, (width, resized_height))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    return gray

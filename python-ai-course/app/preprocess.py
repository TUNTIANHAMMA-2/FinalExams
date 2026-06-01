from __future__ import annotations

import cv2


def prepare_frame(frame, scale: float):
    small = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
    return rgb


def to_ascii_gray(frame, width: int):
    height, original_width = frame.shape[:2]
    ratio = height / max(original_width, 1)
    resized_height = max(1, int(width * ratio * 0.55))
    resized = cv2.resize(frame, (width, resized_height))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    return gray

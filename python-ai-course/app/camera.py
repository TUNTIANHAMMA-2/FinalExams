from __future__ import annotations

import cv2

from app import config


def open_camera():
    capture = cv2.VideoCapture(config.CAMERA_INDEX)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    if not capture.isOpened():
        raise RuntimeError("无法打开摄像头")
    return capture

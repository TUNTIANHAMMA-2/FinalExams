from __future__ import annotations

import cv2

from app import config


def open_camera():
    """打开本机摄像头并设置采集分辨率，返回后续循环读取图像帧的对象。"""
    capture = cv2.VideoCapture(config.CAMERA_INDEX)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    if not capture.isOpened():
        raise RuntimeError("无法打开摄像头")
    return capture

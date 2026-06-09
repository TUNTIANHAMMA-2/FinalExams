from __future__ import annotations

from functools import lru_cache

import cv2


@lru_cache(maxsize=1)
def get_detector():
    """加载并缓存 OpenCV 自带的 Haar 级联人脸检测器。"""
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    if detector.empty():
        raise RuntimeError("无法加载 OpenCV Haar 人脸检测器")
    return detector


def locate_faces(gray_frame):
    """在人脸识别前，从灰度图中检测人脸位置，返回 (x, y, width, height) 列表。"""
    faces = get_detector().detectMultiScale(
        gray_frame,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
    )
    return [tuple(int(value) for value in face) for face in faces]


def largest_face(face_locations):
    """从多个候选人脸中选择面积最大的一张，作为注册样本的主要人脸。"""
    if not face_locations:
        return None
    return max(face_locations, key=lambda face: face[2] * face[3])

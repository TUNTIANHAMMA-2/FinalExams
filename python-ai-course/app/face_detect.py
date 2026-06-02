from __future__ import annotations

from functools import lru_cache

import cv2


@lru_cache(maxsize=1)
def get_detector():
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    if detector.empty():
        raise RuntimeError("无法加载 OpenCV Haar 人脸检测器")
    return detector


def locate_faces(gray_frame):
    faces = get_detector().detectMultiScale(
        gray_frame,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
    )
    return [tuple(int(value) for value in face) for face in faces]


def largest_face(face_locations):
    if not face_locations:
        return None
    return max(face_locations, key=lambda face: face[2] * face[3])

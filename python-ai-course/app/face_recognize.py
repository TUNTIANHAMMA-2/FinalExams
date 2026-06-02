from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from app import config, face_detect, storage


@dataclass
class KnownFace:
    label: int
    user_id: str
    name: str
    sample_path: str


@dataclass
class KnownFaceStore:
    recognizer: object | None
    faces_by_label: dict[int, KnownFace]


def _create_recognizer():
    if not hasattr(cv2, "face") or not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
        raise RuntimeError(
            "当前 OpenCV 缺少 cv2.face 模块。请安装 opencv-contrib-python，而不是 opencv-python。"
        )
    return cv2.face.LBPHFaceRecognizer_create()


def _sample_path(user_id: str) -> Path:
    return config.FACES_DIR / f"{user_id}.png"


def _load_registry() -> dict:
    return storage.load_json(config.LABELS_FILE, {"next_label": 0, "users": {}})


def _save_registry(registry: dict) -> None:
    storage.save_json(config.LABELS_FILE, registry)


def _normalize_face(gray_frame, location):
    x, y, width, height = location
    face = gray_frame[y : y + height, x : x + width]
    face = cv2.resize(face, config.FACE_IMAGE_SIZE)
    return cv2.equalizeHist(face)


def _load_gray_image(image_path: str):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"无法读取图片: {image_path}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.equalizeHist(gray)


def _registered_faces(registry: dict) -> list[KnownFace]:
    faces = []
    for payload in registry["users"].values():
        faces.append(
            KnownFace(
                label=int(payload["label"]),
                user_id=payload["user_id"],
                name=payload["name"],
                sample_path=payload["sample_path"],
            )
        )
    return faces


def rebuild_model() -> None:
    registry = _load_registry()
    faces = _registered_faces(registry)
    samples = []
    labels = []

    for face in faces:
        sample_path = Path(face.sample_path)
        if not sample_path.exists():
            continue
        sample = cv2.imread(str(sample_path), cv2.IMREAD_GRAYSCALE)
        if sample is None:
            continue
        samples.append(sample)
        labels.append(face.label)

    if not samples:
        return

    recognizer = _create_recognizer()
    recognizer.train(samples, np.array(labels, dtype=np.int32))
    config.MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    recognizer.write(str(config.MODEL_FILE))


def register_face(user_id: str, name: str, image_path: str) -> None:
    storage.ensure_data_dirs()
    gray = _load_gray_image(image_path)
    face_locations = face_detect.locate_faces(gray)
    face_location = face_detect.largest_face(face_locations)
    if face_location is None:
        raise ValueError("未在图片中检测到可用人脸")

    normalized = _normalize_face(gray, face_location)
    sample_path = _sample_path(user_id)
    cv2.imwrite(str(sample_path), normalized)

    registry = _load_registry()
    existing = registry["users"].get(user_id)
    label = int(existing["label"]) if existing else int(registry["next_label"])
    if existing is None:
        registry["next_label"] = label + 1

    registry["users"][user_id] = {
        "label": label,
        "user_id": user_id,
        "name": name,
        "sample_path": str(sample_path),
    }
    _save_registry(registry)
    rebuild_model()


def load_known_faces() -> KnownFaceStore:
    storage.ensure_data_dirs()
    registry = _load_registry()
    faces = _registered_faces(registry)
    faces_by_label = {face.label: face for face in faces}
    if not config.MODEL_FILE.exists() or not faces_by_label:
        return KnownFaceStore(recognizer=None, faces_by_label=faces_by_label)

    recognizer = _create_recognizer()
    recognizer.read(str(config.MODEL_FILE))
    return KnownFaceStore(recognizer=recognizer, faces_by_label=faces_by_label)


def match_faces(gray_frame, face_locations, known_faces: KnownFaceStore, threshold: float):
    if not face_locations:
        return []

    results = []

    for location in face_locations:
        if known_faces.recognizer is None:
            results.append({"location": location, "matched": False, "name": "Unknown", "user_id": ""})
            continue

        sample = _normalize_face(gray_frame, location)
        label, confidence = known_faces.recognizer.predict(sample)
        face = known_faces.faces_by_label.get(int(label))
        matched = face is not None and float(confidence) <= threshold
        results.append(
            {
                "location": location,
                "matched": matched,
                "name": face.name if face else "Unknown",
                "user_id": face.user_id if face else "",
                "confidence": float(confidence),
            }
        )
    return results

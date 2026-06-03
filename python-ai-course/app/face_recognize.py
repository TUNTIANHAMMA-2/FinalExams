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
    sample_paths: list[str]


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


def _sample_dir(user_id: str) -> Path:
    return config.FACES_DIR / user_id


def _sample_path(user_id: str, index: int = 1) -> Path:
    return _sample_dir(user_id) / f"sample_{index:03d}.png"


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
        sample_paths = payload.get("sample_paths")
        if not isinstance(sample_paths, list):
            sample_path = payload.get("sample_path", "")
            sample_paths = [sample_path] if sample_path else []
        faces.append(
            KnownFace(
                label=int(payload["label"]),
                user_id=payload["user_id"],
                name=payload["name"],
                sample_paths=[str(path) for path in sample_paths],
            )
        )
    return faces


def rebuild_model() -> None:
    registry = _load_registry()
    faces = _registered_faces(registry)
    samples = []
    labels = []

    for face in faces:
        for sample_path_value in face.sample_paths:
            sample_path = Path(sample_path_value)
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
    register_face_samples(user_id, name, [image_path])


def register_face_samples(user_id: str, name: str, image_paths: list[str]) -> None:
    storage.ensure_data_dirs()
    if not image_paths:
        raise ValueError("至少需要 1 张人脸样本")

    normalized_faces = []
    for index, image_path in enumerate(image_paths, start=1):
        gray = _load_gray_image(image_path)
        face_locations = face_detect.locate_faces(gray)
        face_location = face_detect.largest_face(face_locations)
        if face_location is None:
            raise ValueError(f"第 {index} 张图片未检测到可用人脸")
        normalized_faces.append(_normalize_face(gray, face_location))

    registry = _load_registry()
    existing = registry["users"].get(user_id)
    label = int(existing["label"]) if existing else int(registry["next_label"])
    if existing is None:
        registry["next_label"] = label + 1

    sample_dir = _sample_dir(user_id)
    sample_dir.mkdir(parents=True, exist_ok=True)
    sample_paths = []
    for index, normalized in enumerate(normalized_faces, start=1):
        sample_path = _sample_path(user_id, index)
        if not cv2.imwrite(str(sample_path), normalized):
            raise ValueError(f"第 {index} 张人脸样本保存失败")
        sample_paths.append(str(sample_path))

    registry["users"][user_id] = {
        "label": label,
        "user_id": user_id,
        "name": name,
        "sample_paths": sample_paths,
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


def list_registered_faces() -> list[dict[str, object]]:
    """Return registered users and whether their normalized sample exists."""
    registry = _load_registry()
    users = []
    for face in _registered_faces(registry):
        users.append(
            {
                "label": face.label,
                "user_id": face.user_id,
                "name": face.name,
                "sample_exists": any(Path(sample_path).exists() for sample_path in face.sample_paths),
                "sample_count": sum(1 for sample_path in face.sample_paths if Path(sample_path).exists()),
            }
        )
    return users


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

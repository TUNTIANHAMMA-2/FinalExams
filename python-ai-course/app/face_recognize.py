from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import face_recognition
import numpy as np

from app import config, storage


@dataclass
class KnownFace:
    user_id: str
    name: str
    encoding: list[float]


def encoding_path(user_id: str) -> Path:
    return config.ENCODINGS_DIR / f"{user_id}.json"


def encode_image(image_path: str) -> list[float]:
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if not encodings:
        raise ValueError("未在图片中检测到可用人脸")
    return encodings[0].tolist()


def register_face(user_id: str, name: str, image_path: str) -> None:
    storage.ensure_data_dirs()
    encoding = encode_image(image_path)
    storage.save_json(
        encoding_path(user_id),
        {"user_id": user_id, "name": name, "encoding": encoding},
    )


def load_known_faces() -> list[KnownFace]:
    storage.ensure_data_dirs()
    faces: list[KnownFace] = []
    for path in config.ENCODINGS_DIR.glob("*.json"):
        payload = storage.load_json(path, {})
        if payload:
            faces.append(
                KnownFace(
                    user_id=payload["user_id"],
                    name=payload["name"],
                    encoding=payload["encoding"],
                )
            )
    return faces


def match_faces(rgb_frame, face_locations, known_faces: list[KnownFace], threshold: float):
    if not face_locations:
        return []

    current_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    results = []
    known_vectors = [np.array(face.encoding) for face in known_faces]

    for location, current_encoding in zip(face_locations, current_encodings):
        if not known_vectors:
            results.append({"location": location, "matched": False, "name": "Unknown", "user_id": ""})
            continue

        distances = face_recognition.face_distance(known_vectors, current_encoding)
        best_index = int(np.argmin(distances))
        best_distance = float(distances[best_index])
        matched = best_distance <= threshold
        face = known_faces[best_index] if matched else None
        results.append(
            {
                "location": location,
                "matched": matched,
                "name": face.name if face else "Unknown",
                "user_id": face.user_id if face else "",
                "distance": best_distance,
            }
        )
    return results

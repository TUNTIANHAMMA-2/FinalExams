from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from app import config


def ensure_data_dirs() -> None:
    for path in (
        config.DATA_DIR,
        config.FACES_DIR,
        config.ENCODINGS_DIR,
        config.EXPORTS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def append_attendance(row: dict[str, str]) -> None:
    ensure_data_dirs()
    file_exists = config.ATTENDANCE_FILE.exists()
    with config.ATTENDANCE_FILE.open("a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["date", "time", "user_id", "name", "status"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def read_attendance() -> list[dict[str, str]]:
    if not config.ATTENDANCE_FILE.exists():
        return []
    with config.ATTENDANCE_FILE.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from app import config


ATTENDANCE_FIELDS = ["date", "time", "user_id", "name", "status", "confidence", "event_id"]
EVENT_LOG_FIELDS = [
    "event_id",
    "timestamp",
    "event_type",
    "user_id",
    "name",
    "confidence",
    "face_count",
    "message",
]


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


def _ensure_csv_schema(path: Path, fields: list[str]) -> None:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames == fields:
            return
        rows = [{field: row.get(field, "") for field in fields} for row in reader]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def append_attendance(row: dict[str, str]) -> None:
    ensure_data_dirs()
    _ensure_csv_schema(config.ATTENDANCE_FILE, ATTENDANCE_FIELDS)
    file_exists = config.ATTENDANCE_FILE.exists()
    with config.ATTENDANCE_FILE.open("a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=ATTENDANCE_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({field: row.get(field, "") for field in ATTENDANCE_FIELDS})


def read_attendance() -> list[dict[str, str]]:
    if not config.ATTENDANCE_FILE.exists():
        return []
    with config.ATTENDANCE_FILE.open("r", encoding="utf-8", newline="") as file:
        rows = []
        for row in csv.DictReader(file):
            rows.append({field: row.get(field, "") for field in ATTENDANCE_FIELDS})
        return rows


def append_event(row: dict[str, str]) -> None:
    ensure_data_dirs()
    _ensure_csv_schema(config.EVENT_LOG_FILE, EVENT_LOG_FIELDS)
    file_exists = config.EVENT_LOG_FILE.exists()
    with config.EVENT_LOG_FILE.open("a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=EVENT_LOG_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({field: row.get(field, "") for field in EVENT_LOG_FIELDS})


def read_events() -> list[dict[str, str]]:
    if not config.EVENT_LOG_FILE.exists():
        return []
    with config.EVENT_LOG_FILE.open("r", encoding="utf-8", newline="") as file:
        rows = []
        for row in csv.DictReader(file):
            rows.append({field: row.get(field, "") for field in EVENT_LOG_FIELDS})
        return rows

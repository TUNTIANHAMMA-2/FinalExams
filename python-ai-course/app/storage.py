from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path
from typing import Any
from contextlib import closing

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

META_ATTENDANCE_IMPORTED = "legacy_attendance_csv_imported"
META_EVENTS_IMPORTED = "legacy_event_log_csv_imported"


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


def _connect() -> sqlite3.Connection:
    ensure_data_dirs()
    connection = sqlite3.connect(config.DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def _init_db(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            confidence TEXT NOT NULL DEFAULT '',
            event_id TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS event_log (
            event_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            user_id TEXT NOT NULL DEFAULT '',
            name TEXT NOT NULL DEFAULT '',
            confidence TEXT NOT NULL DEFAULT '',
            face_count TEXT NOT NULL DEFAULT '0',
            message TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS storage_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_attendance_user_date ON attendance(user_id, date);
        CREATE INDEX IF NOT EXISTS idx_attendance_status ON attendance(status);
        CREATE INDEX IF NOT EXISTS idx_event_log_type ON event_log(event_type);
        CREATE INDEX IF NOT EXISTS idx_event_log_timestamp ON event_log(timestamp);
        """
    )


def _meta_value(connection: sqlite3.Connection, key: str) -> str | None:
    row = connection.execute("SELECT value FROM storage_meta WHERE key = ?", (key,)).fetchone()
    return str(row["value"]) if row else None


def _set_meta_value(connection: sqlite3.Connection, key: str, value: str) -> None:
    connection.execute(
        "INSERT OR REPLACE INTO storage_meta(key, value) VALUES(?, ?)",
        (key, value),
    )


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


def _read_csv_rows(path: Path, fields: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        return []
    _ensure_csv_schema(path, fields)
    with path.open("r", encoding="utf-8", newline="") as file:
        return [{field: row.get(field, "") for field in fields} for row in csv.DictReader(file)]


def _import_legacy_csv(connection: sqlite3.Connection) -> None:
    if _meta_value(connection, META_ATTENDANCE_IMPORTED) != "1":
        for row in _read_csv_rows(config.ATTENDANCE_FILE, ATTENDANCE_FIELDS):
            connection.execute(
                """
                INSERT INTO attendance(date, time, user_id, name, status, confidence, event_id)
                VALUES(:date, :time, :user_id, :name, :status, :confidence, :event_id)
                """,
                {field: row.get(field, "") for field in ATTENDANCE_FIELDS},
            )
        _set_meta_value(connection, META_ATTENDANCE_IMPORTED, "1")

    if _meta_value(connection, META_EVENTS_IMPORTED) != "1":
        for row in _read_csv_rows(config.EVENT_LOG_FILE, EVENT_LOG_FIELDS):
            connection.execute(
                """
                INSERT OR IGNORE INTO event_log(
                    event_id, timestamp, event_type, user_id, name, confidence, face_count, message
                )
                VALUES(:event_id, :timestamp, :event_type, :user_id, :name, :confidence, :face_count, :message)
                """,
                {field: row.get(field, "") for field in EVENT_LOG_FIELDS},
            )
        _set_meta_value(connection, META_EVENTS_IMPORTED, "1")


def _ensure_db_ready(connection: sqlite3.Connection) -> None:
    _init_db(connection)
    _import_legacy_csv(connection)
    connection.commit()


def initialize_database() -> None:
    with closing(_connect()) as connection:
        _ensure_db_ready(connection)
        connection.commit()


def append_attendance(row: dict[str, str]) -> None:
    with closing(_connect()) as connection:
        _ensure_db_ready(connection)
        payload = {field: row.get(field, "") for field in ATTENDANCE_FIELDS}
        connection.execute(
            """
            INSERT INTO attendance(date, time, user_id, name, status, confidence, event_id)
            VALUES(:date, :time, :user_id, :name, :status, :confidence, :event_id)
            """,
            payload,
        )
        connection.commit()


def read_attendance() -> list[dict[str, str]]:
    with closing(_connect()) as connection:
        _ensure_db_ready(connection)
        rows = connection.execute(
            """
            SELECT date, time, user_id, name, status, confidence, event_id
            FROM attendance
            ORDER BY date DESC, time DESC, id DESC
            """
        ).fetchall()
        return [{field: str(row[field] or "") for field in ATTENDANCE_FIELDS} for row in rows]


def append_event(row: dict[str, str]) -> None:
    with closing(_connect()) as connection:
        _ensure_db_ready(connection)
        payload = {field: row.get(field, "") for field in EVENT_LOG_FIELDS}
        connection.execute(
            """
            INSERT OR REPLACE INTO event_log(
                event_id, timestamp, event_type, user_id, name, confidence, face_count, message
            )
            VALUES(:event_id, :timestamp, :event_type, :user_id, :name, :confidence, :face_count, :message)
            """,
            payload,
        )
        connection.commit()


def read_events() -> list[dict[str, str]]:
    with closing(_connect()) as connection:
        _ensure_db_ready(connection)
        rows = connection.execute(
            """
            SELECT event_id, timestamp, event_type, user_id, name, confidence, face_count, message
            FROM event_log
            ORDER BY timestamp DESC, event_id DESC
            """
        ).fetchall()
        return [{field: str(row[field] or "") for field in EVENT_LOG_FIELDS} for row in rows]


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def export_attendance_csv(path: Path | None = None) -> Path:
    output_path = path or config.EXPORTS_DIR / "attendance_records.csv"
    write_csv(output_path, ATTENDANCE_FIELDS, read_attendance())
    return output_path


def export_events_csv(path: Path | None = None) -> Path:
    output_path = path or config.EXPORTS_DIR / "recognition_events.csv"
    write_csv(output_path, EVENT_LOG_FIELDS, read_events())
    return output_path

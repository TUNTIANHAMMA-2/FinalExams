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
    """确保项目运行所需的数据、样本、模型和导出目录都已存在。"""
    for path in (
        config.DATA_DIR,
        config.FACES_DIR,
        config.ENCODINGS_DIR,
        config.EXPORTS_DIR,
        config.MODELS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default: Any) -> Any:
    """读取 JSON 文件；文件不存在时返回调用方提供的默认值。"""
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, payload: Any) -> None:
    """以 UTF-8 JSON 格式保存结构化数据，主要用于标签注册表。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def _connect() -> sqlite3.Connection:
    """创建 SQLite 连接，并让查询结果可以按字段名读取。"""
    ensure_data_dirs()
    connection = sqlite3.connect(config.DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def _init_db(connection: sqlite3.Connection) -> None:
    """初始化系统用到的 SQLite 表和索引。"""
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

        CREATE TABLE IF NOT EXISTS students (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL DEFAULT 'AI-1'
        );

        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            subject TEXT NOT NULL,
            exam_name TEXT NOT NULL,
            score REAL NOT NULL,
            exam_date TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS ml_training_samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            attendance_rate_30d REAL NOT NULL,
            late_count_7d INTEGER NOT NULL,
            absent_count_30d INTEGER NOT NULL,
            duplicate_count_30d INTEGER NOT NULL,
            avg_score REAL NOT NULL,
            score_delta REAL NOT NULL,
            risk_label INTEGER NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_attendance_user_date ON attendance(user_id, date);
        CREATE INDEX IF NOT EXISTS idx_attendance_status ON attendance(status);
        CREATE INDEX IF NOT EXISTS idx_event_log_type ON event_log(event_type);
        CREATE INDEX IF NOT EXISTS idx_event_log_timestamp ON event_log(timestamp);
        CREATE INDEX IF NOT EXISTS idx_grades_user_date ON grades(user_id, exam_date);
        CREATE INDEX IF NOT EXISTS idx_ml_training_label ON ml_training_samples(risk_label);
        """
    )


def _meta_value(connection: sqlite3.Connection, key: str) -> str | None:
    """读取存储迁移元信息，用于判断历史 CSV 是否已导入。"""
    row = connection.execute("SELECT value FROM storage_meta WHERE key = ?", (key,)).fetchone()
    return str(row["value"]) if row else None


def _set_meta_value(connection: sqlite3.Connection, key: str, value: str) -> None:
    """写入存储迁移元信息，避免重复导入历史 CSV。"""
    connection.execute(
        "INSERT OR REPLACE INTO storage_meta(key, value) VALUES(?, ?)",
        (key, value),
    )


def _ensure_csv_schema(path: Path, fields: list[str]) -> None:
    """把旧 CSV 文件补齐为当前字段顺序，便于迁移到 SQLite。"""
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
    """按指定字段读取 CSV 行，不存在时返回空列表。"""
    if not path.exists():
        return []
    _ensure_csv_schema(path, fields)
    with path.open("r", encoding="utf-8", newline="") as file:
        return [{field: row.get(field, "") for field in fields} for row in csv.DictReader(file)]


def _import_legacy_csv(connection: sqlite3.Connection) -> None:
    """把早期版本保存的 CSV 签到和事件数据迁移进 SQLite。"""
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
    """确保数据库结构已创建，且历史 CSV 数据已完成一次性迁移。"""
    _init_db(connection)
    _import_legacy_csv(connection)
    connection.commit()


def initialize_database() -> None:
    """显式初始化数据库，供测试或启动流程提前创建表结构。"""
    with closing(_connect()) as connection:
        _ensure_db_ready(connection)
        connection.commit()


def execute_write(sql: str, parameters: tuple[Any, ...] | dict[str, Any] = ()) -> None:
    """执行单条写 SQL，供学生分析模块批量准备数据时复用。"""
    with closing(_connect()) as connection:
        _ensure_db_ready(connection)
        connection.execute(sql, parameters)
        connection.commit()


def execute_many(sql: str, rows: list[tuple[Any, ...]] | list[dict[str, Any]]) -> None:
    """执行批量写 SQL，减少演示数据生成时的重复连接和提交。"""
    with closing(_connect()) as connection:
        _ensure_db_ready(connection)
        connection.executemany(sql, rows)
        connection.commit()


def query(sql: str, parameters: tuple[Any, ...] | dict[str, Any] = ()) -> list[dict[str, Any]]:
    """执行查询 SQL，并把结果转换成普通字典列表。"""
    with closing(_connect()) as connection:
        _ensure_db_ready(connection)
        rows = connection.execute(sql, parameters).fetchall()
        return [dict(row) for row in rows]


def append_attendance(row: dict[str, str]) -> None:
    """追加一条真实生效的签到记录。"""
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
    """按时间倒序读取签到记录，供前端列表和统计分析使用。"""
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
    """写入或更新一条识别事件日志。"""
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
    """按时间倒序读取识别事件，供记录页面和统计分析使用。"""
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
    """把字典列表导出为带表头的 CSV 文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in fields} for row in rows)


def export_attendance_csv(path: Path | None = None) -> Path:
    """导出签到记录 CSV，并返回生成的文件路径。"""
    output_path = path or config.EXPORTS_DIR / "attendance_records.csv"
    write_csv(output_path, ATTENDANCE_FIELDS, read_attendance())
    return output_path


def export_events_csv(path: Path | None = None) -> Path:
    """导出识别事件 CSV，并返回生成的文件路径。"""
    output_path = path or config.EXPORTS_DIR / "recognition_events.csv"
    write_csv(output_path, EVENT_LOG_FIELDS, read_events())
    return output_path

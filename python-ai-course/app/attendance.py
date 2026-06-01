from __future__ import annotations

from datetime import datetime

from app import storage


def mark_attendance(user_id: str, name: str) -> dict[str, str]:
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    for row in storage.read_attendance():
        if row["date"] == current_date and row["user_id"] == user_id:
            return {
                "date": current_date,
                "time": current_time,
                "user_id": user_id,
                "name": name,
                "status": "duplicate",
            }

    record = {
        "date": current_date,
        "time": current_time,
        "user_id": user_id,
        "name": name,
        "status": "success",
    }
    storage.append_attendance(record)
    return record

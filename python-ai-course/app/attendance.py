from __future__ import annotations

from datetime import datetime

from app import storage


def mark_attendance(
    user_id: str,
    name: str,
    confidence: str = "",
    event_id: str = "",
) -> dict[str, str]:
    """写入一次有效签到；同一用户同一天重复识别时只返回 duplicate，不重复入库。"""
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
                "confidence": confidence,
                "event_id": event_id,
            }

    record = {
        "date": current_date,
        "time": current_time,
        "user_id": user_id,
        "name": name,
        "status": "success",
        "confidence": confidence,
        "event_id": event_id,
    }
    storage.append_attendance(record)
    return record

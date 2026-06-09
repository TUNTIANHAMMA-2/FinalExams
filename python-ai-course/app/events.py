from __future__ import annotations

from datetime import datetime
from itertools import count

from app import storage

_COUNTER = count()


def next_event_id(now: datetime | None = None) -> str:
    """生成带时间戳的识别事件编号，用于关联签到记录和识别日志。"""
    current = now or datetime.now()
    return f"{current.strftime('%Y%m%d%H%M%S%f')}-{next(_COUNTER):04d}"


def append_event(
    event_type: str,
    user_id: str = "",
    name: str = "",
    confidence: str = "",
    face_count: int = 0,
    message: str = "",
    event_id: str | None = None,
) -> dict[str, str]:
    """记录一次识别事件，如成功、重复签到、未知人脸或未训练模型。"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = {
        "event_id": event_id or next_event_id(),
        "timestamp": timestamp,
        "event_type": event_type,
        "user_id": user_id,
        "name": name,
        "confidence": confidence,
        "face_count": str(face_count),
        "message": message,
    }
    storage.append_event(row)
    return row

from __future__ import annotations

from collections import Counter

from app import config, storage


def _safe_rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(min(numerator / denominator, 1.0), 4)


def summarize_attendance() -> dict[str, object]:
    rows = storage.read_attendance()
    events = storage.read_events()
    by_status = Counter(row["status"] for row in rows)
    by_event_type = Counter(event["event_type"] for event in events)
    registered_users = storage.load_json(config.LABELS_FILE, {"users": {}}).get("users", {})
    registered_user_ids = set(registered_users)

    valid_success_rows = [
        row
        for row in rows
        if row["status"] == "success" and row["user_id"] in registered_user_ids
    ]
    by_valid_status = Counter(row["status"] for row in valid_success_rows)
    by_user = Counter(row["name"] for row in valid_success_rows)

    success_user_ids = {row["user_id"] for row in valid_success_rows}
    recognition_success_events = sum(
        by_event_type.get(event_type, 0)
        for event_type in ("success", "duplicate", "recognized")
    )
    recognition_attempts = recognition_success_events + by_event_type.get("unknown", 0)
    return {
        "total_records": len(rows),
        "status_counts": dict(by_status),
        "valid_status_counts": dict(by_valid_status),
        "event_total": len(events),
        "event_counts": dict(by_event_type),
        "user_counts": dict(by_user),
        "registered_user_count": len(registered_users),
        "attendance_rate": _safe_rate(len(success_user_ids), len(registered_users)),
        "recognition_success_rate": _safe_rate(
            recognition_success_events,
            recognition_attempts,
        ),
    }

from __future__ import annotations

from collections import Counter

from app import storage


def summarize_attendance() -> dict[str, object]:
    rows = storage.read_attendance()
    by_status = Counter(row["status"] for row in rows)
    by_user = Counter(row["name"] for row in rows if row["status"] == "success")
    return {
        "total_records": len(rows),
        "status_counts": dict(by_status),
        "user_counts": dict(by_user),
    }

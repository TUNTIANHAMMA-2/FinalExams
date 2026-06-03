from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from app import analytics, config, events, storage


class EventLogTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.original_attendance = config.ATTENDANCE_FILE
        self.original_event_log = config.EVENT_LOG_FILE
        self.original_labels = config.LABELS_FILE
        root = Path(self.temp_dir.name)
        config.ATTENDANCE_FILE = root / "attendance.csv"
        config.EVENT_LOG_FILE = root / "event_log.csv"
        config.LABELS_FILE = root / "labels.json"

    def tearDown(self) -> None:
        config.ATTENDANCE_FILE = self.original_attendance
        config.EVENT_LOG_FILE = self.original_event_log
        config.LABELS_FILE = self.original_labels
        self.temp_dir.cleanup()

    def test_event_log_is_included_in_summary(self) -> None:
        storage.save_json(
            config.LABELS_FILE,
            {
                "users": {
                    "2026001": {"name": "Test User"},
                    "2026002": {"name": "Second User"},
                }
            },
        )
        storage.append_attendance(
            {
                "date": "2026-06-03",
                "time": "10:00:00",
                "user_id": "2026001",
                "name": "Test User",
                "status": "success",
                "confidence": "12.3",
                "event_id": "evt-1",
            }
        )
        events.append_event("success", user_id="2026001", name="Test User", event_id="evt-1")
        events.append_event("duplicate", user_id="2026001", name="Test User", event_id="evt-2")
        events.append_event("recognized", user_id="2026002", name="Second User", event_id="evt-3")
        events.append_event("unknown", face_count=1, event_id="evt-4")

        summary = analytics.summarize_attendance()

        self.assertEqual(
            summary["event_counts"],
            {"success": 1, "duplicate": 1, "recognized": 1, "unknown": 1},
        )
        self.assertEqual(summary["registered_user_count"], 2)
        self.assertEqual(summary["attendance_rate"], 0.5)
        self.assertEqual(summary["recognition_success_rate"], 0.75)

    def test_legacy_attendance_schema_is_upgraded_before_append(self) -> None:
        config.ATTENDANCE_FILE.write_text(
            "date,time,user_id,name,status\n2026-06-03,10:00:00,2026001,Test User,success\n",
            encoding="utf-8",
        )

        storage.append_attendance(
            {
                "date": "2026-06-03",
                "time": "10:05:00",
                "user_id": "2026002",
                "name": "Second User",
                "status": "success",
                "confidence": "21.5",
                "event_id": "evt-2",
            }
        )

        rows = storage.read_attendance()

        self.assertEqual(rows[0]["confidence"], "")
        self.assertEqual(rows[0]["event_id"], "")
        self.assertEqual(rows[1]["confidence"], "21.5")
        self.assertEqual(rows[1]["event_id"], "evt-2")


if __name__ == "__main__":
    unittest.main()

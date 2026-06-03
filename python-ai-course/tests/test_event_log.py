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
        self.original_database = config.DATABASE_FILE
        self.original_exports = config.EXPORTS_DIR
        root = Path(self.temp_dir.name)
        config.ATTENDANCE_FILE = root / "attendance.csv"
        config.EVENT_LOG_FILE = root / "event_log.csv"
        config.LABELS_FILE = root / "labels.json"
        config.DATABASE_FILE = root / "attendance.db"
        config.EXPORTS_DIR = root / "exports"

    def tearDown(self) -> None:
        config.ATTENDANCE_FILE = self.original_attendance
        config.EVENT_LOG_FILE = self.original_event_log
        config.LABELS_FILE = self.original_labels
        config.DATABASE_FILE = self.original_database
        config.EXPORTS_DIR = self.original_exports
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

    def test_attendance_rate_ignores_unregistered_legacy_records(self) -> None:
        storage.save_json(
            config.LABELS_FILE,
            {"users": {"2026002": {"name": "Second User"}}},
        )
        storage.append_attendance(
            {
                "date": "2026-06-01",
                "time": "10:00:00",
                "user_id": "2026001",
                "name": "Legacy User",
                "status": "success",
            }
        )
        storage.append_attendance(
            {
                "date": "2026-06-03",
                "time": "10:05:00",
                "user_id": "2026002",
                "name": "Second User",
                "status": "success",
            }
        )

        summary = analytics.summarize_attendance()

        self.assertEqual(summary["status_counts"], {"success": 2})
        self.assertEqual(summary["valid_status_counts"], {"success": 1})
        self.assertEqual(summary["user_counts"], {"Second User": 1})
        self.assertEqual(summary["registered_user_count"], 1)
        self.assertEqual(summary["attendance_rate"], 1.0)

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
        rows_by_user = {row["user_id"]: row for row in rows}

        self.assertEqual(rows_by_user["2026001"]["confidence"], "")
        self.assertEqual(rows_by_user["2026001"]["event_id"], "")
        self.assertEqual(rows_by_user["2026002"]["confidence"], "21.5")
        self.assertEqual(rows_by_user["2026002"]["event_id"], "evt-2")

    def test_export_csv_writes_sqlite_rows(self) -> None:
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

        attendance_path = storage.export_attendance_csv()
        events_path = storage.export_events_csv()

        self.assertTrue(attendance_path.exists())
        self.assertTrue(events_path.exists())
        self.assertIn("Test User", attendance_path.read_text(encoding="utf-8-sig"))
        self.assertIn("success", events_path.read_text(encoding="utf-8-sig"))


if __name__ == "__main__":
    unittest.main()

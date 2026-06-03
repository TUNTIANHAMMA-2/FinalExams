from __future__ import annotations

import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from app import attendance, config


class AttendanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.original_file = config.ATTENDANCE_FILE
        self.original_database = config.DATABASE_FILE
        root = Path(self.temp_dir.name)
        config.ATTENDANCE_FILE = root / "attendance.csv"
        config.DATABASE_FILE = root / "attendance.db"

    def tearDown(self) -> None:
        config.ATTENDANCE_FILE = self.original_file
        config.DATABASE_FILE = self.original_database
        self.temp_dir.cleanup()

    def test_mark_attendance_blocks_duplicate_for_same_day(self) -> None:
        first = attendance.mark_attendance("2026001", "Test User", confidence="12.3", event_id="evt-1")
        second = attendance.mark_attendance("2026001", "Test User", confidence="12.3", event_id="evt-2")

        self.assertEqual(first["status"], "success")
        self.assertEqual(first["confidence"], "12.3")
        self.assertEqual(first["event_id"], "evt-1")
        self.assertEqual(second["status"], "duplicate")


if __name__ == "__main__":
    unittest.main()

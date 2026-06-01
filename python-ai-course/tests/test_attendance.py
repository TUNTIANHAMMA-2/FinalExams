from __future__ import annotations

import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from app import attendance, config


class AttendanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.original_file = config.ATTENDANCE_FILE
        config.ATTENDANCE_FILE = Path(self.temp_dir.name) / "attendance.csv"

    def tearDown(self) -> None:
        config.ATTENDANCE_FILE = self.original_file
        self.temp_dir.cleanup()

    def test_mark_attendance_blocks_duplicate_for_same_day(self) -> None:
        first = attendance.mark_attendance("2026001", "Test User")
        second = attendance.mark_attendance("2026001", "Test User")

        self.assertEqual(first["status"], "success")
        self.assertEqual(second["status"], "duplicate")


if __name__ == "__main__":
    unittest.main()

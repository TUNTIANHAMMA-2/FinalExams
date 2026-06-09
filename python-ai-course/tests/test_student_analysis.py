from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from app import config, storage, student_analysis


class StudentAnalysisTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.originals = {
            "DATA_DIR": config.DATA_DIR,
            "FACES_DIR": config.FACES_DIR,
            "ENCODINGS_DIR": config.ENCODINGS_DIR,
            "EXPORTS_DIR": config.EXPORTS_DIR,
            "MODELS_DIR": config.MODELS_DIR,
            "ATTENDANCE_FILE": config.ATTENDANCE_FILE,
            "EVENT_LOG_FILE": config.EVENT_LOG_FILE,
            "DATABASE_FILE": config.DATABASE_FILE,
            "LABELS_FILE": config.LABELS_FILE,
            "MODEL_FILE": config.MODEL_FILE,
            "STUDENT_RISK_MODEL_FILE": config.STUDENT_RISK_MODEL_FILE,
        }
        root = Path(self.temp_dir.name)
        config.DATA_DIR = root / "data"
        config.FACES_DIR = config.DATA_DIR / "faces"
        config.ENCODINGS_DIR = config.DATA_DIR / "encodings"
        config.EXPORTS_DIR = config.DATA_DIR / "exports"
        config.MODELS_DIR = config.DATA_DIR / "models"
        config.ATTENDANCE_FILE = config.DATA_DIR / "attendance.csv"
        config.EVENT_LOG_FILE = config.DATA_DIR / "event_log.csv"
        config.DATABASE_FILE = config.DATA_DIR / "attendance.db"
        config.LABELS_FILE = config.ENCODINGS_DIR / "labels.json"
        config.MODEL_FILE = config.ENCODINGS_DIR / "lbph_model.yml"
        config.STUDENT_RISK_MODEL_FILE = config.MODELS_DIR / "student_risk_model.joblib"

    def tearDown(self) -> None:
        for key, value in self.originals.items():
            setattr(config, key, value)
        self.temp_dir.cleanup()

    def test_generate_demo_data_writes_students_grades_events_and_training_rows(self) -> None:
        generated = student_analysis.generate_demo_data()

        self.assertEqual(generated["students"], 5)
        self.assertEqual(generated["grades"], 10)
        self.assertGreater(generated["attendance_records"], 100)
        self.assertEqual(generated["training_samples"], 85)
        self.assertEqual(storage.query("SELECT COUNT(*) AS count FROM students")[0]["count"], 5)
        self.assertEqual(storage.query("SELECT COUNT(*) AS count FROM grades")[0]["count"], 10)
        self.assertEqual(storage.query("SELECT COUNT(*) AS count FROM ml_training_samples")[0]["count"], 85)

    def test_train_model_persists_decision_tree_model(self) -> None:
        student_analysis.generate_demo_data()

        result = student_analysis.train_model()

        self.assertTrue(config.STUDENT_RISK_MODEL_FILE.exists())
        self.assertEqual(result["training_samples"], 85)
        self.assertEqual(result["features"], student_analysis.FEATURES)
        self.assertIn("高风险", result["label_counts"])

    def test_analyze_students_returns_risk_reports(self) -> None:
        student_analysis.generate_demo_data()
        student_analysis.train_model()

        result = student_analysis.analyze_students()

        self.assertTrue(result["model_ready"])
        self.assertEqual(result["student_count"], 5)
        self.assertEqual(result["training_samples"], 85)
        self.assertEqual(len(result["students"]), 5)
        self.assertIn("高风险", result["risk_counts"])
        high_risk_students = [row for row in result["students"] if row["risk_level"] == "高风险"]
        self.assertGreaterEqual(len(high_risk_students), 1)
        self.assertIn("系统评估", result["students"][0]["summary"])

    def test_analyze_students_does_not_generate_demo_data_on_read(self) -> None:
        result = student_analysis.analyze_students()

        self.assertFalse(result["model_ready"])
        self.assertEqual(result["student_count"], 0)
        self.assertEqual(result["training_samples"], 0)
        self.assertEqual(result["students"], [])
        self.assertEqual(storage.query("SELECT COUNT(*) AS count FROM students")[0]["count"], 0)


if __name__ == "__main__":
    unittest.main()

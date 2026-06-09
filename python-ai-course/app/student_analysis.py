from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from random import Random
from typing import Any

import joblib
import numpy as np
from sklearn.tree import DecisionTreeClassifier

from app import config, storage


FEATURES = [
    "attendance_rate_30d",
    "late_count_7d",
    "absent_count_30d",
    "duplicate_count_30d",
    "avg_score",
    "score_delta",
]

RISK_LABELS = {
    0: "低风险",
    1: "中风险",
    2: "高风险",
}


@dataclass(frozen=True)
class DemoStudent:
    """演示班级中的固定学生画像，用于可重复生成训练和预测数据。"""

    user_id: str
    name: str
    class_name: str
    profile: str
    base_score: int
    second_score: int
    attendance_rate: float
    late_count: int
    duplicate_count: int


DEMO_STUDENTS = [
    DemoStudent("2026001", "张三", "AI-1", "stable", 86, 88, 0.96, 0, 0),
    DemoStudent("2026002", "李四", "AI-1", "mild", 82, 76, 0.84, 2, 1),
    DemoStudent("2026003", "王五", "AI-1", "high", 79, 62, 0.67, 4, 2),
    DemoStudent("2026004", "赵六", "AI-1", "grade_drop", 91, 80, 0.92, 1, 0),
    DemoStudent("2026005", "陈晨", "AI-1", "attendance_drop", 74, 72, 0.73, 3, 1),
]


def _risk_label(attendance_rate: float, late_count: int, score_delta: float) -> int:
    """根据出勤、迟到和成绩变化生成训练样本的风险标签。"""
    score = 0
    if attendance_rate < 0.8:
        score += 30
    elif attendance_rate < 0.9:
        score += 15

    if late_count >= 3:
        score += 30
    elif late_count >= 1:
        score += 15

    if score_delta <= -10:
        score += 40
    elif score_delta <= -5:
        score += 20

    if score >= 60:
        return 2
    if score >= 30:
        return 1
    return 0


def _risk_score(features: dict[str, float]) -> int:
    """把学生特征转换成 0-100 的风险分数，便于前端展示。"""
    score = 0
    attendance_rate = float(features["attendance_rate_30d"])
    late_count = int(features["late_count_7d"])
    score_delta = float(features["score_delta"])

    if attendance_rate < 0.8:
        score += 30
    elif attendance_rate < 0.9:
        score += 15

    if late_count >= 3:
        score += 30
    elif late_count >= 1:
        score += 15

    if score_delta <= -10:
        score += 40
    elif score_delta <= -5:
        score += 20

    return min(score, 100)


def generate_demo_data() -> dict[str, int]:
    """生成确定性的演示学生、成绩、签到、事件日志和机器学习训练样本。"""
    random = Random(20260603)
    today = date.today()
    demo_user_ids = [student.user_id for student in DEMO_STUDENTS]
    placeholders = ",".join("?" for _ in demo_user_ids)
    attendance_rows: list[tuple[Any, ...]] = []
    event_rows: list[tuple[Any, ...]] = []
    training_rows: list[tuple[Any, ...]] = []

    storage.execute_write(f"DELETE FROM students WHERE user_id IN ({placeholders})", tuple(demo_user_ids))
    storage.execute_write(f"DELETE FROM grades WHERE user_id IN ({placeholders})", tuple(demo_user_ids))
    storage.execute_write(
        f"DELETE FROM ml_training_samples WHERE user_id IN ({placeholders}) OR user_id LIKE 'synthetic-%'",
        tuple(demo_user_ids),
    )
    storage.execute_write("DELETE FROM attendance WHERE event_id LIKE 'demo-%'")
    storage.execute_write("DELETE FROM event_log WHERE event_id LIKE 'demo-%'")

    storage.execute_many(
        "INSERT INTO students(user_id, name, class_name) VALUES(?, ?, ?)",
        [(student.user_id, student.name, student.class_name) for student in DEMO_STUDENTS],
    )

    grade_rows = []
    for student in DEMO_STUDENTS:
        grade_rows.append((student.user_id, "人工智能基础", "期中考试", student.base_score, str(today - timedelta(days=30))))
        grade_rows.append((student.user_id, "人工智能基础", "阶段测验", student.second_score, str(today - timedelta(days=3))))

        # 用预设出勤率反推出 30 天内的到课/缺勤分布，形成可解释的演示数据。
        present_days = round(student.attendance_rate * 30)
        absent_days = 30 - present_days
        absent_indexes = set(random.sample(range(30), absent_days))
        present_indexes = [index for index in range(30) if index not in absent_indexes]
        recent_present_indexes = [index for index in present_indexes if index >= 23]
        late_source = recent_present_indexes or present_indexes
        late_days = set(random.sample(late_source, min(student.late_count, len(late_source))))
        for day_index in present_indexes:
            current = today - timedelta(days=29 - day_index)
            is_late = day_index in late_days
            checkin_time = "08:42:00" if is_late else "08:12:00"
            event_id = f"demo-att-{student.user_id}-{day_index:02d}"
            attendance_rows.append((str(current), checkin_time, student.user_id, student.name, "success", "", event_id))
            event_rows.append((event_id, f"{current} {checkin_time}", "success", student.user_id, student.name, "", "1", "演示签到记录"))

        for index in range(student.duplicate_count):
            current = today - timedelta(days=index + 1)
            event_rows.append((
                f"demo-dup-{student.user_id}-{index:02d}",
                f"{current} 08:50:00",
                "duplicate",
                student.user_id,
                student.name,
                "",
                "1",
                "演示重复签到事件",
            ))

        extracted_attendance_rate = present_days / 30
        score_delta = student.second_score - student.base_score
        label = _risk_label(extracted_attendance_rate, student.late_count, score_delta)
        training_rows.append((
            student.user_id,
            extracted_attendance_rate,
            student.late_count,
            absent_days,
            student.duplicate_count,
            (student.base_score + student.second_score) / 2,
            score_delta,
            label,
        ))

    # 额外生成合成样本，避免决策树只学习到 5 个演示学生的固定模式。
    for index in range(80):
        attendance_rate = random.uniform(0.55, 1.0)
        late_count = random.randint(0, 6)
        absent_count = max(0, round((1 - attendance_rate) * 30))
        duplicate_count = random.randint(0, 3)
        avg_score = random.uniform(55, 95)
        score_delta = random.uniform(-18, 6)
        label = _risk_label(attendance_rate, late_count, score_delta)
        training_rows.append((
            f"synthetic-{index:03d}",
            attendance_rate,
            late_count,
            absent_count,
            duplicate_count,
            avg_score,
            score_delta,
            label,
        ))

    storage.execute_many(
        "INSERT INTO grades(user_id, subject, exam_name, score, exam_date) VALUES(?, ?, ?, ?, ?)",
        grade_rows,
    )
    storage.execute_many(
        """
        INSERT INTO attendance(date, time, user_id, name, status, confidence, event_id)
        VALUES(?, ?, ?, ?, ?, ?, ?)
        """,
        attendance_rows,
    )
    storage.execute_many(
        """
        INSERT OR REPLACE INTO event_log(event_id, timestamp, event_type, user_id, name, confidence, face_count, message)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """,
        event_rows,
    )
    storage.execute_many(
        """
        INSERT INTO ml_training_samples(
            user_id, attendance_rate_30d, late_count_7d, absent_count_30d,
            duplicate_count_30d, avg_score, score_delta, risk_label
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """,
        training_rows,
    )

    return {
        "students": len(DEMO_STUDENTS),
        "grades": len(grade_rows),
        "attendance_records": len(attendance_rows),
        "recognition_events": len(event_rows),
        "training_samples": len(training_rows),
    }


def train_model() -> dict[str, Any]:
    """读取训练样本，训练学生风险决策树模型，并保存到本地文件。"""
    rows = storage.query("SELECT * FROM ml_training_samples")
    if len(rows) < 10:
        generate_demo_data()
        rows = storage.query("SELECT * FROM ml_training_samples")

    x = np.array([[float(row[feature]) for feature in FEATURES] for row in rows], dtype=float)
    y = np.array([int(row["risk_label"]) for row in rows], dtype=int)
    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(x, y)

    config.STUDENT_RISK_MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, config.STUDENT_RISK_MODEL_FILE)
    label_counts = {RISK_LABELS.get(label, str(label)): int((y == label).sum()) for label in sorted(set(y))}
    return {
        "training_samples": len(rows),
        "features": FEATURES,
        "label_counts": label_counts,
        "model_path": str(config.STUDENT_RISK_MODEL_FILE),
    }


def _load_model():
    """加载已训练的学生风险模型；未训练时抛出明确错误。"""
    if not config.STUDENT_RISK_MODEL_FILE.exists():
        raise FileNotFoundError("学生风险模型尚未训练")
    return joblib.load(config.STUDENT_RISK_MODEL_FILE)


def _student_features(student: dict[str, Any]) -> dict[str, float]:
    """从签到、事件和成绩表中提取一个学生的风险分析特征。"""
    user_id = str(student["user_id"])
    recent_date = str(date.today() - timedelta(days=6))
    attendance_rows = storage.query(
        "SELECT date, time FROM attendance WHERE user_id = ? AND status = 'success' AND event_id LIKE 'demo-%'",
        (user_id,),
    )
    duplicate_rows = storage.query(
        "SELECT event_id FROM event_log WHERE user_id = ? AND event_type = 'duplicate' AND event_id LIKE 'demo-%'",
        (user_id,),
    )
    grade_rows = storage.query(
        "SELECT score FROM grades WHERE user_id = ? ORDER BY exam_date ASC, id ASC",
        (user_id,),
    )

    present_count = len({row["date"] for row in attendance_rows})
    attendance_rate = present_count / 30
    late_count = sum(
        1
        for row in attendance_rows
        if str(row["date"]) >= recent_date and str(row["time"]) > "08:30:00"
    )
    absent_count = max(0, 30 - present_count)
    duplicate_count = len(duplicate_rows)
    scores = [float(row["score"]) for row in grade_rows]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    score_delta = scores[-1] - scores[-2] if len(scores) >= 2 else 0.0

    return {
        "attendance_rate_30d": round(attendance_rate, 4),
        "late_count_7d": late_count,
        "absent_count_30d": absent_count,
        "duplicate_count_30d": duplicate_count,
        "avg_score": round(avg_score, 2),
        "score_delta": round(score_delta, 2),
    }


def _summary(name: str, features: dict[str, float], risk_level: str) -> tuple[str, str]:
    """根据预测结果生成面向教师的自然语言摘要和处理建议。"""
    attendance_percent = features["attendance_rate_30d"] * 100
    score_delta = features["score_delta"]
    summary = (
        f"{name}近30天出勤率为{attendance_percent:.1f}%，近7天迟到{int(features['late_count_7d'])}次，"
        f"最近一次成绩变化为{score_delta:+.1f}分，系统评估为{risk_level}。"
    )
    if risk_level == "高风险":
        suggestion = "建议老师尽快进行学习状态沟通，并重点关注到课情况和近期成绩变化。"
    elif risk_level == "中风险":
        suggestion = "建议老师持续观察该生出勤与成绩波动，必要时进行提醒。"
    else:
        suggestion = "当前状态较稳定，可维持常规关注。"
    return summary, suggestion


def analyze_students() -> dict[str, Any]:
    """对所有学生提取特征并调用决策树模型，返回前端分析报告。"""
    students = storage.query("SELECT user_id, name, class_name FROM students ORDER BY user_id")
    training_count = int(storage.query("SELECT COUNT(*) AS count FROM ml_training_samples")[0]["count"])
    if not students or not config.STUDENT_RISK_MODEL_FILE.exists():
        return {
            "model_ready": config.STUDENT_RISK_MODEL_FILE.exists(),
            "student_count": len(students),
            "training_samples": training_count,
            "features": FEATURES,
            "risk_counts": {label: 0 for label in RISK_LABELS.values()},
            "students": [],
        }

    model = _load_model()
    reports = []

    for student in students:
        features = _student_features(student)
        x = np.array([[features[feature] for feature in FEATURES]], dtype=float)
        label = int(model.predict(x)[0])
        probabilities = model.predict_proba(x)[0] if hasattr(model, "predict_proba") else []
        confidence = float(max(probabilities)) if len(probabilities) else 0.0
        risk_level = RISK_LABELS.get(label, "未知")
        summary, suggestion = _summary(str(student["name"]), features, risk_level)

        reports.append({
            "user_id": student["user_id"],
            "name": student["name"],
            "class_name": student["class_name"],
            "features": features,
            "risk_label": label,
            "risk_level": risk_level,
            "risk_score": _risk_score(features),
            "confidence": round(confidence, 4),
            "summary": summary,
            "suggestion": suggestion,
        })

    risk_counts: dict[str, int] = {}
    for report in reports:
        risk_counts[report["risk_level"]] = risk_counts.get(report["risk_level"], 0) + 1

    for label in RISK_LABELS.values():
        risk_counts.setdefault(label, 0)

    return {
        "model_ready": config.STUDENT_RISK_MODEL_FILE.exists(),
        "student_count": len(reports),
        "training_samples": training_count,
        "features": FEATURES,
        "risk_counts": risk_counts,
        "students": reports,
    }

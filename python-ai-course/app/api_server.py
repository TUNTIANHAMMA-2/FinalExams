from __future__ import annotations

import base64
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from app import analytics, attendance, config, events, storage

MAX_JSON_BYTES = 10 * 1024 * 1024
DATA_URL_PREFIX = re.compile(r"^data:image/[a-zA-Z0-9.+-]+;base64,")


def _json_error(message: str, status: str = "error") -> dict[str, str]:
    """统一生成前端可展示的 JSON 错误结构。"""
    return {"status": status, "message": message}


def _decode_image_data(image_data: str):
    """把浏览器上传的 data URL 或 base64 图片解码为 OpenCV BGR 图像矩阵。"""
    import cv2
    import numpy as np

    payload = DATA_URL_PREFIX.sub("", image_data.strip(), count=1)
    try:
        raw = base64.b64decode(payload, validate=True)
    except ValueError as exc:
        raise ValueError("图片数据不是有效的 base64 编码") from exc

    image_array = np.frombuffer(raw, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("无法解析图片数据")
    return image


def _write_image_data(image_data: str, output_path: Path) -> None:
    """把浏览器采集的人脸图片保存为文件，供注册训练流程读取。"""
    import cv2

    image = _decode_image_data(image_data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output_path), image):
        raise ValueError("图片保存失败")


def register_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """处理前端注册请求：保存多张样本图片，并触发 LBPH 模型重新训练。"""
    user_id = str(payload.get("user_id", "")).strip()
    name = str(payload.get("name", "")).strip()
    raw_image_list = payload.get("image_data_list")
    if isinstance(raw_image_list, list):
        image_data_list = [str(item).strip() for item in raw_image_list if str(item).strip()]
    else:
        image_data = str(payload.get("image_data", "")).strip()
        image_data_list = [image_data] if image_data else []

    if not user_id or not name or not image_data_list:
        raise ValueError("user_id、name 和 image_data_list 都不能为空")

    from app import face_recognize

    source_paths = []
    for index, image_data in enumerate(image_data_list, start=1):
        source_path = config.FACES_DIR / f"{user_id}_source_{index:03d}.jpg"
        _write_image_data(image_data, source_path)
        source_paths.append(str(source_path))
    face_recognize.register_face_samples(user_id, name, source_paths)
    return {
        "status": "success",
        "user": {"user_id": user_id, "name": name},
        "sample_count": len(source_paths),
        "message": f"人脸注册成功，已使用 {len(source_paths)} 张样本重新训练 LBPH 模型",
    }


def validate_face_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """校验一帧注册样本是否恰好包含一张人脸。"""
    import cv2

    from app import face_detect

    image_data = str(payload.get("image_data", "")).strip()
    if not image_data:
        raise ValueError("image_data 不能为空")

    image = _decode_image_data(image_data)
    # 前端传来的彩色图像先转灰度并均衡化，再送入 Haar 人脸检测器。
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    locations = face_detect.locate_faces(gray)
    face_count = len(locations)

    if face_count == 1:
        message = "检测到 1 张人脸，可以作为训练样本"
        valid = True
    elif face_count == 0:
        message = "未检测到人脸，请调整位置后重新采集"
        valid = False
    else:
        message = "检测到多张人脸，请确保画面中只有本人"
        valid = False

    return {
        "status": "success" if valid else "invalid",
        "valid": valid,
        "face_count": face_count,
        "message": message,
    }


def recognize_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """处理实时识别请求：检测人脸、调用 LBPH 匹配，并按结果写入签到或事件日志。"""
    import cv2

    from app import face_detect, face_recognize

    image_data = str(payload.get("image_data", "")).strip()
    should_mark = bool(payload.get("mark_attendance", True))
    if not image_data:
        raise ValueError("image_data 不能为空")

    image = _decode_image_data(image_data)
    # 识别阶段和注册阶段保持同样的灰度化、均衡化流程，保证输入分布一致。
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    locations = face_detect.locate_faces(gray)
    known_faces = face_recognize.load_known_faces()
    matches = face_recognize.match_faces(
        gray,
        locations,
        known_faces,
        config.LBPH_CONFIDENCE_THRESHOLD,
    )

    normalized_matches = []
    for match in matches:
        normalized = dict(match)
        x, y, width, height = normalized["location"]
        normalized["location"] = {"x": x, "y": y, "width": width, "height": height}
        normalized_matches.append(normalized)

    matched_faces = [match for match in normalized_matches if match["matched"]]
    if matched_faces:
        primary = matched_faces[0]
        confidence = f"{primary.get('confidence', '')}"
        event_id = events.next_event_id()
        preview_record = None
        if should_mark:
            preview_record = attendance.mark_attendance(
                primary["user_id"],
                primary["name"],
                confidence=confidence,
                event_id=event_id,
            )

        result_status = preview_record["status"] if preview_record else "recognized"
        event_message = {
            "success": "签到成功",
            "duplicate": "当天已签到，已拦截重复写入",
            "recognized": "识别成功，仅预览未写入签到",
        }[result_status]
        event_row = events.append_event(
            result_status,
            user_id=primary["user_id"],
            name=primary["name"],
            confidence=confidence,
            face_count=len(locations),
            message=event_message,
            event_id=event_id,
        )
        if preview_record:
            primary["attendance"] = preview_record
        primary["event"] = event_row
    elif not locations:
        primary = None
        result_status = "no_face"
        event_row = None
    elif known_faces.recognizer is None:
        primary = None
        result_status = "no_model"
        event_row = events.append_event(
            "no_model",
            face_count=len(locations),
            message="检测到人脸，但尚未训练识别模型",
        )
    else:
        primary = None
        result_status = "unknown"
        confidence = ""
        if normalized_matches:
            confidence = f"{normalized_matches[0].get('confidence', '')}"
        event_row = events.append_event(
            "unknown",
            confidence=confidence,
            face_count=len(locations),
            message="检测到人脸，但未匹配到注册用户",
        )

    return {
        "status": result_status,
        "face_count": len(locations),
        "event": event_row,
        "primary_match": primary,
        "matches": normalized_matches,
    }


class ApiRequestHandler(BaseHTTPRequestHandler):
    """为 React 前端提供本地 HTTP API 的请求处理器。"""

    def _send_json(self, status_code: int, payload: dict[str, Any] | list[Any]) -> None:
        """发送 JSON 响应，并允许前端开发服务器跨域访问。"""
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _send_csv_file(self, path: Path, filename: str) -> None:
        """发送 CSV 文件下载响应。"""
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/csv; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        """读取并解析 JSON 请求体，同时限制最大上传体积。"""
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            return {}
        if content_length > MAX_JSON_BYTES:
            raise ValueError("请求体过大")
        raw_body = self.rfile.read(content_length)
        return json.loads(raw_body.decode("utf-8"))

    def do_OPTIONS(self) -> None:
        """响应浏览器 CORS 预检请求。"""
        self._send_json(200, {"status": "ok"})

    def do_GET(self) -> None:
        """处理查询类接口，如签到记录、事件日志、统计结果和学生分析。"""
        path = urlparse(self.path).path
        try:
            if path == "/api/health":
                self._send_json(200, {"status": "ok"})
            elif path == "/api/records":
                self._send_json(200, {"records": storage.read_attendance()})
            elif path == "/api/events":
                self._send_json(200, {"events": storage.read_events()})
            elif path == "/api/export/attendance":
                self._send_csv_file(storage.export_attendance_csv(), "attendance_records.csv")
            elif path == "/api/export/events":
                self._send_csv_file(storage.export_events_csv(), "recognition_events.csv")
            elif path == "/api/stats":
                self._send_json(200, analytics.summarize_attendance())
            elif path == "/api/student-analysis":
                from app import student_analysis

                self._send_json(200, student_analysis.analyze_students())
            elif path == "/api/users":
                from app import face_recognize

                self._send_json(200, {"users": face_recognize.list_registered_faces()})
            else:
                self._send_json(404, _json_error("接口不存在", "not_found"))
        except Exception as exc:  # pragma: no cover - defensive HTTP boundary
            self._send_json(500, _json_error(str(exc)))

    def do_POST(self) -> None:
        """处理会改变状态的接口，如注册、人脸识别、生成演示数据和训练模型。"""
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
            if path == "/api/register":
                self._send_json(200, register_from_payload(payload))
            elif path == "/api/validate-face":
                self._send_json(200, validate_face_from_payload(payload))
            elif path == "/api/recognize":
                self._send_json(200, recognize_from_payload(payload))
            elif path in ("/api/student-analysis/demo-data", "/api/demo-data"):
                from app import student_analysis

                generated = student_analysis.generate_demo_data()
                model = student_analysis.train_model()
                self._send_json(
                    200,
                    {
                        "status": "success",
                        "message": "演示班级数据已生成，并已重新训练学生风险模型",
                        "generated": generated,
                        "model": model,
                    },
                )
            elif path in ("/api/student-analysis/train", "/api/ml/train"):
                from app import student_analysis

                model = student_analysis.train_model()
                self._send_json(
                    200,
                    {
                        "status": "success",
                        "message": "学生风险模型训练完成",
                        "model": model,
                    },
                )
            else:
                self._send_json(404, _json_error("接口不存在", "not_found"))
        except ValueError as exc:
            self._send_json(400, _json_error(str(exc)))
        except Exception as exc:  # pragma: no cover - defensive HTTP boundary
            self._send_json(500, _json_error(str(exc)))


def run_server(host: str, port: int) -> None:
    """启动供 React 前端调用的本地 API 服务。"""
    storage.ensure_data_dirs()
    server = ThreadingHTTPServer((host, port), ApiRequestHandler)
    print(f"API server running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAPI server stopped.")
    finally:
        server.server_close()

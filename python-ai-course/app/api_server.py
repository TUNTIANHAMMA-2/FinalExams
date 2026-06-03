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
    return {"status": status, "message": message}


def _decode_image_data(image_data: str):
    """Decode a browser data URL or raw base64 string into an OpenCV BGR image."""
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
    """Persist a browser image data URL for the OpenCV registration pipeline."""
    import cv2

    image = _decode_image_data(image_data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output_path), image):
        raise ValueError("图片保存失败")


def register_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Register a face from JSON payload sent by the browser."""
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


def recognize_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Recognize a browser image frame and optionally write attendance."""
    import cv2

    from app import face_detect, face_recognize

    image_data = str(payload.get("image_data", "")).strip()
    should_mark = bool(payload.get("mark_attendance", True))
    if not image_data:
        raise ValueError("image_data 不能为空")

    image = _decode_image_data(image_data)
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
    def _send_json(self, status_code: int, payload: dict[str, Any] | list[Any]) -> None:
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
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            return {}
        if content_length > MAX_JSON_BYTES:
            raise ValueError("请求体过大")
        raw_body = self.rfile.read(content_length)
        return json.loads(raw_body.decode("utf-8"))

    def do_OPTIONS(self) -> None:
        self._send_json(200, {"status": "ok"})

    def do_GET(self) -> None:
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
            elif path == "/api/users":
                from app import face_recognize

                self._send_json(200, {"users": face_recognize.list_registered_faces()})
            else:
                self._send_json(404, _json_error("接口不存在", "not_found"))
        except Exception as exc:  # pragma: no cover - defensive HTTP boundary
            self._send_json(500, _json_error(str(exc)))

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
            if path == "/api/register":
                self._send_json(200, register_from_payload(payload))
            elif path == "/api/recognize":
                self._send_json(200, recognize_from_payload(payload))
            else:
                self._send_json(404, _json_error("接口不存在", "not_found"))
        except ValueError as exc:
            self._send_json(400, _json_error(str(exc)))
        except Exception as exc:  # pragma: no cover - defensive HTTP boundary
            self._send_json(500, _json_error(str(exc)))


def run_server(host: str, port: int) -> None:
    """Start the local API server used by the React frontend."""
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

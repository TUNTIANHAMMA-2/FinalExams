from __future__ import annotations

import base64
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from app import analytics, attendance, config, storage

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
    image_data = str(payload.get("image_data", "")).strip()

    if not user_id or not name or not image_data:
        raise ValueError("user_id、name 和 image_data 都不能为空")

    from app import face_recognize

    source_path = config.FACES_DIR / f"{user_id}_source.jpg"
    _write_image_data(image_data, source_path)
    face_recognize.register_face(user_id, name, str(source_path))
    return {
        "status": "success",
        "user": {"user_id": user_id, "name": name},
        "message": "人脸注册成功，LBPH 模型已重新训练",
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
        if normalized["matched"] and should_mark:
            normalized["attendance"] = attendance.mark_attendance(
                normalized["user_id"],
                normalized["name"],
            )
        normalized_matches.append(normalized)

    matched_faces = [match for match in normalized_matches if match["matched"]]
    if matched_faces:
        primary = matched_faces[0]
        record = primary.get("attendance")
        result_status = record["status"] if record else "recognized"
    elif not locations:
        primary = None
        result_status = "no_face"
    elif known_faces.recognizer is None:
        primary = None
        result_status = "no_model"
    else:
        primary = None
        result_status = "unknown"

    return {
        "status": result_status,
        "face_count": len(locations),
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

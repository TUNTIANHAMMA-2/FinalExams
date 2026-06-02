from __future__ import annotations

import unittest

from app import api_server


class ApiServerTest(unittest.TestCase):
    def test_register_payload_requires_identity_and_image(self) -> None:
        with self.assertRaises(ValueError):
            api_server.register_from_payload({"user_id": "", "name": "张三", "image_data": ""})

    def test_json_error_shape(self) -> None:
        self.assertEqual(
            api_server._json_error("failed"),
            {"status": "error", "message": "failed"},
        )


if __name__ == "__main__":
    unittest.main()

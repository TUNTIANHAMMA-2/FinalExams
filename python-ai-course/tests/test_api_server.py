from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app import api_server


class ApiServerTest(unittest.TestCase):
    def test_register_payload_requires_identity_and_image(self) -> None:
        with self.assertRaises(ValueError):
            api_server.register_from_payload({"user_id": "", "name": "张三", "image_data": ""})

    def test_register_payload_accepts_three_training_samples(self) -> None:
        write_image = Mock()
        register_samples = Mock()
        fake_face_recognize = SimpleNamespace(register_face_samples=register_samples)

        with (
            patch("app.api_server._write_image_data", write_image),
            patch.dict("sys.modules", {"app.face_recognize": fake_face_recognize}),
        ):
            response = api_server.register_from_payload(
                {
                    "user_id": "2026001",
                    "name": "Test User",
                    "image_data_list": ["sample-1", "sample-2", "sample-3"],
                }
            )

        self.assertEqual(write_image.call_count, 3)
        register_samples.assert_called_once()
        self.assertEqual(register_samples.call_args.args[0], "2026001")
        self.assertEqual(register_samples.call_args.args[1], "Test User")
        self.assertEqual(len(register_samples.call_args.args[2]), 3)
        self.assertEqual(response["sample_count"], 3)

    def test_validate_face_requires_exactly_one_face(self) -> None:
        fake_cv2 = SimpleNamespace(
            COLOR_BGR2GRAY=0,
            cvtColor=Mock(return_value="gray"),
            equalizeHist=Mock(return_value="equalized"),
        )
        fake_face_detect = SimpleNamespace(locate_faces=Mock(return_value=[]))

        with (
            patch("app.api_server._decode_image_data", Mock(return_value="image")),
            patch.dict("sys.modules", {"cv2": fake_cv2, "app.face_detect": fake_face_detect}),
        ):
            no_face = api_server.validate_face_from_payload({"image_data": "sample"})
            fake_face_detect.locate_faces.return_value = [(1, 2, 3, 4)]
            one_face = api_server.validate_face_from_payload({"image_data": "sample"})
            fake_face_detect.locate_faces.return_value = [(1, 2, 3, 4), (5, 6, 7, 8)]
            multi_face = api_server.validate_face_from_payload({"image_data": "sample"})

        self.assertFalse(no_face["valid"])
        self.assertEqual(no_face["face_count"], 0)
        self.assertTrue(one_face["valid"])
        self.assertEqual(one_face["face_count"], 1)
        self.assertFalse(multi_face["valid"])
        self.assertEqual(multi_face["face_count"], 2)

    def test_json_error_shape(self) -> None:
        self.assertEqual(
            api_server._json_error("failed"),
            {"status": "error", "message": "failed"},
        )


if __name__ == "__main__":
    unittest.main()

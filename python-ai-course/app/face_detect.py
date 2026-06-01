from __future__ import annotations

import face_recognition


def locate_faces(rgb_frame):
    return face_recognition.face_locations(rgb_frame)

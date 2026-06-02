from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FACES_DIR = DATA_DIR / "faces"
ENCODINGS_DIR = DATA_DIR / "encodings"
EXPORTS_DIR = DATA_DIR / "exports"
ATTENDANCE_FILE = DATA_DIR / "attendance.csv"
LABELS_FILE = ENCODINGS_DIR / "labels.json"
MODEL_FILE = ENCODINGS_DIR / "lbph_model.yml"

CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FRAME_SCALE = 0.25
FACE_IMAGE_SIZE = (200, 200)
LBPH_CONFIDENCE_THRESHOLD = 75.0
ASCII_WIDTH = 80
ASCII_CHARS = "@#S%?*+;:,. "

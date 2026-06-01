from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FACES_DIR = DATA_DIR / "faces"
ENCODINGS_DIR = DATA_DIR / "encodings"
EXPORTS_DIR = DATA_DIR / "exports"
ATTENDANCE_FILE = DATA_DIR / "attendance.csv"

CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FRAME_SCALE = 0.25
MATCH_THRESHOLD = 0.48
ASCII_WIDTH = 80
ASCII_CHARS = "@#S%?*+;:,. "

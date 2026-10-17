import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.getenv("EVIDORA_DATA_DIR", ROOT / "data"))
UPLOADS = DATA / "uploads"
DB = DATA / "evidora.sqlite3"
DATA.mkdir(parents=True, exist_ok=True)
UPLOADS.mkdir(parents=True, exist_ok=True)

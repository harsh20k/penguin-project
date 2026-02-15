import os
from pathlib import Path

DEV_MODE = os.getenv("DEV_MODE", "true").lower() == "true"
DB_PATH = os.getenv("DB_PATH", str(Path(__file__).resolve().parent.parent / "local.db"))

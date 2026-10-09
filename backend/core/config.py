"""RansomGuard AI - Core Configuration Module.

Loads system configuration from environment variables with sensible defaults
for local development and academic demonstrations.
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Configurable paths
PROTECTED_DIRECTORY = Path(os.getenv("PROTECTED_DIRECTORY", str(BASE_DIR / "protected_storage"))).resolve()
SNAPSHOT_DIRECTORY = Path(os.getenv("SNAPSHOT_DIRECTORY", str(BASE_DIR / "snapshots"))).resolve()
LOGS_DIRECTORY = Path(os.getenv("LOGS_DIRECTORY", str(BASE_DIR / "logs"))).resolve()
DATABASE_DIR = Path(BASE_DIR / "backend" / "database").resolve()
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(DATABASE_DIR / "ransomguard.db"))).resolve()

# Server Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

# Monitoring & Detection Thresholds
MONITOR_ENABLED = os.getenv("MONITOR_ENABLED", "True").lower() in ("true", "1", "t")
ENTROPY_THRESHOLD = float(os.getenv("ENTROPY_THRESHOLD", "7.3"))  # 0 to 8 scale
BURST_MODIFICATION_WINDOW_SEC = int(os.getenv("BURST_MODIFICATION_WINDOW_SEC", "10"))
BURST_MODIFICATION_COUNT = int(os.getenv("BURST_MODIFICATION_COUNT", "8"))
BURST_RENAME_COUNT = int(os.getenv("BURST_RENAME_COUNT", "6"))
BURST_DELETE_COUNT = int(os.getenv("BURST_DELETE_COUNT", "6"))
BURST_OPS_PER_SEC_THRESHOLD = int(os.getenv("BURST_OPS_PER_SEC_THRESHOLD", "12"))

# Known Ransomware Extensions
SUSPICIOUS_EXTENSIONS = {
    ".locked", ".crypto", ".enc", ".crypted", ".ransom", ".wnry",
    ".wncrypt", ".locky", ".crypt", ".cerber", ".zepto", ".lockbit",
    ".blackcat", ".dry", ".encrypted", ".crpt", ".darkside", ".revil"
}

# Ensure base directories exist
for directory in [PROTECTED_DIRECTORY, SNAPSHOT_DIRECTORY, LOGS_DIRECTORY, DATABASE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

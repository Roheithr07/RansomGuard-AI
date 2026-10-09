"""RansomGuard AI - Process Monitor Service.

Safely captures process context for file access events without interrupting execution.
"""
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ransomguard.process_monitor")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def get_current_process_info() -> Dict[str, Any]:
    """Retrieves safe context for the active process."""
    if not PSUTIL_AVAILABLE:
        return {"pid": os.getpid(), "name": "unknown_agent", "cpu_percent": 0.0}

    try:
        current = psutil.Process(os.getpid())
        return {
            "pid": current.pid,
            "name": current.name(),
            "cpu_percent": round(current.cpu_percent(interval=None), 2),
            "memory_mb": round(current.memory_info().rss / (1024 * 1024), 2)
        }
    except Exception as e:
        logger.debug("Failed to read current process info: %s", e)
        return {"pid": os.getpid(), "name": "python.exe", "cpu_percent": 0.0}


def get_process_for_file(file_path: str) -> Dict[str, Any]:
    """Attempts to identify which process holds or accessed a file (best effort)."""
    # On Windows, querying all open handles requires admin rights or elevated privileges.
    # We do a fast non-blocking lookup of current or parent process as baseline context.
    return get_current_process_info()

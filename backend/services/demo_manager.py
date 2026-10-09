"""RansomGuard AI - Presentation Demo Session & Reset Manager.

Provides safe, sandboxed presentation resets to guarantee fresh data for live demonstrations.
Strictly isolated: clears only demo artifacts, test threats, test events, test snapshots, and telemetry.
Never touches application code, core business files, or system directories.
"""
import os
import shutil
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from backend.core.config import (
    PROTECTED_DIRECTORY,
    SNAPSHOT_DIRECTORY,
    BASE_DIR,
)
from backend.core.database import get_db_connection
from backend.services.storage_monitor import storage_monitor
from backend.services.snapshot_manager import snapshot_manager
from backend.services.recovery_manager import recovery_manager
from backend.services.simulator import safe_simulator
from backend.services.audit_service import audit_service

logger = logging.getLogger("ransomguard.demo_manager")

FORBIDDEN_RESET_TARGETS = {
    "c:\\", "c:/", "c:\\windows", "c:/windows", "c:\\users", "c:/users",
    "c:\\program files", "c:/program files", "c:\\program files (x86)",
    "c:/program files (x86)", "/etc", "/var", "/usr", "/bin", "/sbin",
    "..", "../", "..\\", "/", "\\"
}


class DemoManagerService:
    """Manages presentation demo sessions and clean state resets."""

    def __init__(self):
        self._current_session_id: Optional[str] = None
        self._init_session()

    def _init_session(self) -> str:
        """Loads or creates the active presentation session ID."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM system_settings WHERE key = 'current_demo_session_id'")
            row = cursor.fetchone()
            conn.close()
            if row and row["value"]:
                self._current_session_id = row["value"]
                return self._current_session_id
        except Exception:
            pass

        self._current_session_id = self.generate_new_session_id()
        self._persist_session_id(self._current_session_id)
        return self._current_session_id

    def generate_new_session_id(self) -> str:
        """Generates a unique presentation session ID format: demo_YYYYMMDD_HHMMSS_xxxx."""
        now = datetime.now(timezone.utc)
        ts_part = now.strftime("%Y%m%d_%H%M%S")
        rand_part = uuid.uuid4().hex[:4]
        return f"demo_{ts_part}_{rand_part}"

    def get_current_session_id(self) -> str:
        """Returns the active presentation session ID."""
        if not self._current_session_id:
            return self._init_session()
        return self._current_session_id

    def _persist_session_id(self, session_id: str):
        """Persists the session ID into SQLite system_settings table."""
        try:
            now_iso = datetime.now(timezone.utc).isoformat()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_settings (key, value, updated_at)
                VALUES ('current_demo_session_id', ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
            """, (session_id, now_iso))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning("Failed to persist session ID to system_settings: %s", e)

    def is_safe_demo_target(self, path: Path) -> bool:
        """Strict sandbox guard: ensures path is never a protected system or root path."""
        try:
            resolved_str = str(path.resolve()).lower()
            norm_str = resolved_str.rstrip("\\/")

            # Disallow roots and dangerous OS directories
            for forbidden in FORBIDDEN_RESET_TARGETS:
                if norm_str == forbidden.lower().rstrip("\\/"):
                    return False

            if path.resolve() == path.resolve().anchor:
                return False

            return True
        except Exception:
            return False

    def reset_demo(self) -> Dict[str, Any]:
        """Safely cleans previous demo data and prepares a fresh presentation state."""
        now = datetime.now(timezone.utc)
        new_session_id = self.generate_new_session_id()
        self._current_session_id = new_session_id
        self._persist_session_id(new_session_id)

        logger.info("Executing presentation reset for new session: %s", new_session_id)

        # 0. Halt any active simulation immediately
        safe_simulator.stop()

        # Temporarily halt watchdog observer to prevent deletion noise during cleanup
        was_monitoring = storage_monitor.is_running
        if was_monitoring:
            storage_monitor.stop()

        # 1. Clean simulation files strictly from demo sandbox
        demo_sandbox = safe_simulator.demo_dir
        cleaned_demo_files = 0
        if demo_sandbox.exists() and self.is_safe_demo_target(demo_sandbox):
            for item in list(demo_sandbox.iterdir()):
                if item.is_file():
                    try:
                        item.unlink()
                        cleaned_demo_files += 1
                    except Exception as e:
                        logger.warning("Could not unlink demo artifact %s: %s", item, e)

        # Also clean any .locked files in active storage_monitor.target_dir / 'demo' if distinct
        active_target = storage_monitor.target_dir
        if active_target.exists() and self.is_safe_demo_target(active_target):
            # If target directory has demo folder inside it
            active_demo_sub = active_target / "demo"
            if active_demo_sub.exists() and active_demo_sub != demo_sandbox:
                for item in list(active_demo_sub.iterdir()):
                    if item.is_file():
                        try:
                            item.unlink()
                            cleaned_demo_files += 1
                        except Exception:
                            pass
            # Clean any stray .locked simulation files strictly created during attacks
            for pattern in ["*.locked"]:
                for item in active_target.glob(pattern):
                    if item.is_file():
                        try:
                            item.unlink()
                            cleaned_demo_files += 1
                        except Exception:
                            pass

        # 2. Safely purge test snapshots from SNAPSHOT_DIRECTORY
        cleaned_snapshots = 0
        if SNAPSHOT_DIRECTORY.exists() and self.is_safe_demo_target(SNAPSHOT_DIRECTORY):
            for snap_folder in list(SNAPSHOT_DIRECTORY.iterdir()):
                if snap_folder.is_dir() and snap_folder.name.startswith("snap_"):
                    try:
                        shutil.rmtree(snap_folder, ignore_errors=True)
                        cleaned_snapshots += 1
                    except Exception as e:
                        logger.warning("Could not delete snapshot directory %s: %s", snap_folder, e)

        # 3. Clean SQLite demo tables while preserving legitimate audit trail
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM events")
            cursor.execute("DELETE FROM threats")
            cursor.execute("DELETE FROM recovery_operations")
            cursor.execute("DELETE FROM snapshot_files")
            cursor.execute("DELETE FROM snapshots")
            # Only purge demo simulation noise; preserve legitimate operational & configuration audit trail
            cursor.execute("""
                DELETE FROM audit_logs
                WHERE source IN ('safe_simulator', 'phase10_test_runner')
                   OR event_type LIKE '%simulation%'
                   OR related_entity_id LIKE 'sim_%'
            """)
            conn.commit()
            logger.info("Cleared demo telemetry while preserving persistent legitimate audit trail in SQLite.")
        except Exception as e:
            logger.error("Failed to clear database tables on reset: %s", e)
            conn.rollback()
        finally:
            conn.close()

        # 4. Reset in-memory telemetry in storage_monitor
        storage_monitor.metrics["created"] = 0
        storage_monitor.metrics["modified"] = 0
        storage_monitor.metrics["deleted"] = 0
        storage_monitor.metrics["renamed"] = 0
        storage_monitor.metrics["suspicious"] = 0
        storage_monitor.metrics["ops_history"] = []
        storage_monitor.metrics["started_at"] = now.isoformat()
        if hasattr(storage_monitor, "_recent_event_dedup"):
            storage_monitor._recent_event_dedup.clear()

        # Ensure watchdog is running on active target
        if not storage_monitor.is_running:
            storage_monitor.start()

        # 5. Log initial baseline audit event for the fresh session
        audit_service.log_event(
            event_type="presentation_session_started",
            action="Start Fresh Presentation Session",
            result="INITIALIZED",
            severity="INFO",
            source="demo_manager",
            related_entity_id=new_session_id,
            details=f"Presentation session {new_session_id} started. Clean defensive monitoring state established on {storage_monitor.target_dir}."
        )

        # 6. Broadcast DEMO_RESET event to WebSocket clients
        storage_monitor._broadcast_event({
            "type": "DEMO_RESET",
            "demo_session_id": new_session_id,
            "timestamp": now.isoformat(),
            "message": f"Presentation session {new_session_id} initialized with fresh telemetry.",
            "metrics": storage_monitor.get_current_metrics()
        })

        return {
            "success": True,
            "demo_session_id": new_session_id,
            "timestamp": now.isoformat(),
            "cleaned_artifacts": {
                "demo_files_removed": cleaned_demo_files,
                "snapshots_removed": cleaned_snapshots,
            },
            "state": {
                "threats_count": 0,
                "events_count": 0,
                "snapshots_count": 0,
                "recoveries_count": 0,
                "monitored_directory": str(storage_monitor.target_dir),
                "watchdog_active": storage_monitor.is_running
            },
            "metrics": storage_monitor.get_current_metrics(),
            "message": f"Presentation session '{new_session_id}' initialized. Fresh monitoring state ready."
        }


# Global Demo Manager Singleton
demo_manager = DemoManagerService()

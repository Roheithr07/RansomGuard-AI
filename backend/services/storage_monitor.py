"""RansomGuard AI - Filesystem Storage Monitor Service.

Utilizes Python watchdog to monitor protected directories in real-time.
Processes filesystem events, extracts file metadata, evaluates risk through
the RiskEngine, persists records to SQLite, and broadcasts live telemetry to WebSocket clients.
"""
import os
import uuid
import json
import time
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    FileCreatedEvent,
    FileModifiedEvent,
    FileDeletedEvent,
    FileMovedEvent,
)

from backend.core.config import PROTECTED_DIRECTORY
from backend.core.database import get_db_connection
from backend.core.websocket import ws_manager
from backend.services.risk_engine import risk_engine
from backend.services.process_monitor import get_process_for_file
from backend.services.audit_service import audit_service

logger = logging.getLogger("ransomguard.monitor")


class StorageEventHandler(FileSystemEventHandler):
    """Handles raw filesystem events dispatched by watchdog observer."""

    def __init__(self, monitor_service):
        super().__init__()
        self.monitor = monitor_service

    def on_created(self, event):
        if not event.is_directory:
            self.monitor.process_event("created", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.monitor.process_event("modified", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.monitor.process_event("deleted", event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.monitor.process_event("renamed", event.dest_path, old_path=event.src_path)


class StorageMonitorService:
    """Manages the watchdog observer lifecycle and event dispatching."""

    def __init__(self, target_directory: Optional[Path] = None):
        self.target_dir = Path(target_directory or PROTECTED_DIRECTORY).resolve()
        self.observer: Optional[Observer] = None
        self.is_running: bool = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # Real-time operational metrics
        self.metrics = {
            "created": 0,
            "modified": 0,
            "deleted": 0,
            "renamed": 0,
            "suspicious": 0,
            "ops_history": [],  # list of timestamps
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        self._recent_event_dedup: Dict[str, float] = {}

    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        """Sets the asyncio event loop for WebSocket broadcasting from watchdog threads."""
        self._loop = loop

    def start(self) -> bool:
        """Starts monitoring the target directory and demo sandbox."""
        if self.is_running:
            logger.info("Storage monitor is already active.")
            return True

        self.target_dir.mkdir(parents=True, exist_ok=True)
        handler = StorageEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(handler, str(self.target_dir), recursive=True)

        # Also schedule safe demo sandbox if distinct from target_dir
        try:
            demo_dir = (Path(PROTECTED_DIRECTORY) / "demo").resolve()
            demo_dir.mkdir(parents=True, exist_ok=True)
            if self.target_dir != demo_dir and not demo_dir.is_relative_to(self.target_dir):
                self.observer.schedule(handler, str(demo_dir), recursive=True)
                logger.info("Watchdog also monitoring simulation sandbox: %s", demo_dir)
        except Exception as e:
            logger.debug("Could not schedule demo_dir watch: %s", e)

        self.observer.start()
        self.is_running = True
        logger.info("Watchdog storage monitoring started on: %s", self.target_dir)
        audit_service.log_event(
            event_type="monitoring_started",
            action="Start Watchdog Filesystem Monitor",
            result="ACTIVE",
            severity="INFO",
            source="storage_monitor",
            related_entity_id=str(self.target_dir),
            details=f"Watchdog filesystem monitoring active on {self.target_dir}"
        )
        self._broadcast_event({
            "type": "MONITORING_STATUS",
            "is_monitoring": True,
            "metrics": self.get_current_metrics()
        })
        return True

    def stop(self) -> bool:
        """Stops the watchdog observer."""
        if not self.is_running or not self.observer:
            return False

        try:
            self.observer.stop()
            self.observer.join(timeout=3.0)
            self.is_running = False
            logger.info("Watchdog storage monitoring stopped.")
            audit_service.log_event(
                event_type="monitoring_stopped",
                action="Stop Watchdog Filesystem Monitor",
                result="SUSPENDED",
                severity="WARNING",
                source="storage_monitor",
                related_entity_id=str(self.target_dir),
                details=f"Watchdog filesystem monitoring stopped on {self.target_dir}"
            )
            self._broadcast_event({
                "type": "MONITORING_STATUS",
                "is_monitoring": False,
                "metrics": self.get_current_metrics()
            })
            return True
        except Exception as e:
            logger.error("Error stopping storage observer: %s", e)
            return False

    def process_event(self, event_type: str, file_path: str, old_path: Optional[str] = None):
        """Processes and enriches a filesystem event, computes risk, and persists."""
        try:
            path_obj = Path(file_path).resolve()
            # Ignore internal application files, databases, source code, snapshots, or temp files
            if (
                path_obj.name.startswith(".~")
                or path_obj.name.endswith(".tmp.swp")
                or path_obj.suffix.lower() in [".db", ".db-wal", ".db-shm", ".sqlite", ".sqlite-wal", ".sqlite-shm", ".pyc"]
                or any(part in ["backend", "database", "snapshots", "logs", ".git", ".agents", "__pycache__"] for part in path_obj.parts)
            ):
                return

            now_ts = time.time()
            dedup_key = f"{event_type}:{str(path_obj)}"
            if dedup_key in self._recent_event_dedup and (now_ts - self._recent_event_dedup[dedup_key]) < 0.25:
                return
            self._recent_event_dedup[dedup_key] = now_ts

            now_iso = datetime.now(timezone.utc).isoformat()
            event_id = f"evt-{uuid.uuid4().hex[:12]}"
            ext = path_obj.suffix.lower()

            # File size and entropy calculation
            file_size = 0
            entropy = 0.0
            if event_type != "deleted" and path_obj.exists():
                try:
                    file_size = path_obj.stat().st_size
                    entropy = risk_engine.calculate_entropy(file_path)
                except Exception as e:
                    logger.debug("Could not inspect file attributes for %s: %s", file_path, e)

            # Process context
            proc_info = get_process_for_file(file_path)
            proc_id = proc_info.get("pid")
            proc_name = proc_info.get("name", "explorer.exe")

            # Risk Engine Evaluation
            risk_result = risk_engine.evaluate_event(
                event_type=event_type,
                file_path=file_path,
                entropy=entropy,
                old_path=old_path
            )

            risk_score = risk_result["risk_score"]
            severity = risk_result["severity"]
            reasons = risk_result["reasons"]

            status = "flagged" if risk_score >= 60 else "recorded"
            if risk_score >= 80:
                status = "blocked"

            # Update in-memory metrics
            self.metrics["ops_history"].append(now_ts)
            # Prune ops older than 60s
            cutoff = now_ts - 60.0
            self.metrics["ops_history"] = [t for t in self.metrics["ops_history"] if t >= cutoff]

            if event_type == "created":
                self.metrics["created"] += 1
            elif event_type == "modified":
                self.metrics["modified"] += 1
            elif event_type == "deleted":
                self.metrics["deleted"] += 1
            elif event_type in ("renamed", "moved"):
                self.metrics["renamed"] += 1

            if risk_score >= 60:
                self.metrics["suspicious"] += 1

            # Store in SQLite
            self._save_event(
                event_id=event_id,
                timestamp=now_iso,
                event_type=event_type,
                file_path=str(path_obj),
                file_name=path_obj.name,
                extension=ext,
                file_size=file_size,
                entropy=entropy,
                proc_id=proc_id,
                proc_name=proc_name,
                risk_score=risk_score,
                severity=severity,
                reasons=reasons,
                status=status
            )

            # Check if a threat record should be created/updated
            if risk_score >= 60:
                self._create_or_update_threat(
                    timestamp=now_iso,
                    severity=severity,
                    risk_score=risk_score,
                    reasons=reasons,
                    file_path=str(path_obj),
                    proc_info=proc_info
                )

            # Broadcast to WebSocket
            event_payload = {
                "type": "FILE_EVENT",
                "data": {
                    "event_id": event_id,
                    "timestamp": now_iso,
                    "event_type": event_type,
                    "file_path": str(path_obj),
                    "file_name": path_obj.name,
                    "extension": ext,
                    "file_size": file_size,
                    "entropy": entropy,
                    "process_name": proc_name,
                    "risk_score": risk_score,
                    "severity": severity,
                    "reasons": reasons,
                    "status": status,
                },
                "metrics": self.get_current_metrics()
            }

            self._broadcast_event(event_payload)

        except Exception as e:
            logger.error("Error processing filesystem event for %s: %s", file_path, e, exc_info=True)

    def _save_event(
        self,
        event_id: str,
        timestamp: str,
        event_type: str,
        file_path: str,
        file_name: str,
        extension: str,
        file_size: int,
        entropy: float,
        proc_id: Optional[int],
        proc_name: str,
        risk_score: int,
        severity: str,
        reasons: list,
        status: str
    ):
        """Persists file event record to SQLite."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (
                    event_id, timestamp, event_type, file_path, file_name,
                    extension, file_size, entropy, process_id, process_name,
                    risk_score, severity, detection_reasons, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id, timestamp, event_type, file_path, file_name,
                extension, file_size, entropy, proc_id, proc_name,
                risk_score, severity, json.dumps(reasons), status
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error("Failed to insert event into database: %s", e)

    def _create_or_update_threat(
        self,
        timestamp: str,
        severity: str,
        risk_score: int,
        reasons: list,
        file_path: str,
        proc_info: dict
    ):
        """Creates or updates an active threat incident record in threats table."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if there is an active uncontained threat from recent seconds
            cursor.execute("""
                SELECT id, threat_id, severity, risk_score, detection_reasons, affected_files, file_count, timestamp
                FROM threats
                WHERE status != 'Resolved'
                ORDER BY id DESC
                LIMIT 1
            """)
            recent_threat = cursor.fetchone()
            should_update = False
            if recent_threat:
                try:
                    th_time = datetime.fromisoformat(recent_threat["timestamp"].replace("Z", "+00:00"))
                    curr_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    if abs((curr_time - th_time).total_seconds()) <= 15:
                        should_update = True
                except Exception:
                    pass

            if should_update and recent_threat:
                threat_id = recent_threat["threat_id"]
                try:
                    aff_files = json.loads(recent_threat["affected_files"])
                except Exception:
                    aff_files = []
                if file_path not in aff_files:
                    aff_files.append(file_path)

                try:
                    det_reasons = json.loads(recent_threat["detection_reasons"])
                except Exception:
                    det_reasons = []
                for r in reasons:
                    if r not in det_reasons:
                        det_reasons.append(r)

                new_risk = max(recent_threat["risk_score"], risk_score)
                new_sev = "CRITICAL" if new_risk >= 80 else ("HIGH" if new_risk >= 60 else severity)

                cursor.execute("""
                    UPDATE threats
                    SET severity = ?, risk_score = ?, detection_reasons = ?, affected_files = ?, file_count = ?, timestamp = ?
                    WHERE id = ?
                """, (
                    new_sev,
                    new_risk,
                    json.dumps(det_reasons),
                    json.dumps(aff_files),
                    len(aff_files),
                    timestamp,
                    recent_threat["id"]
                ))
                conn.commit()
                conn.close()
                logger.warning("Threat alert updated: %s (Risk Score: %d, Files: %d)", threat_id, new_risk, len(aff_files))
                return

            threat_id = f"thr-{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT INTO threats (
                    threat_id, timestamp, severity, risk_score,
                    detection_reasons, affected_files, file_count,
                    process_info, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                threat_id,
                timestamp,
                severity,
                risk_score,
                json.dumps(reasons),
                json.dumps([file_path]),
                1,
                json.dumps(proc_info),
                "Detected"
            ))
            conn.commit()
            conn.close()
            logger.warning("Threat alert registered: %s (Risk Score: %d, Severity: %s)", threat_id, risk_score, severity)

            audit_service.log_event(
                event_type="threat_detected",
                action="Detect Ransomware Pattern",
                result="ALERT_GENERATED",
                severity=severity,
                source="ransomware_detector",
                related_entity_id=threat_id,
                details=f"Risk Score {risk_score}/100. Reasons: {', '.join(reasons)}. File: {file_path}"
            )
        except Exception as e:
            logger.error("Failed to create threat record: %s", e)

    def _broadcast_event(self, payload: dict):
        """Dispatches payload to WebSocket clients safely via event loop."""
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(ws_manager.broadcast(payload), self._loop)

    def get_current_metrics(self) -> Dict[str, Any]:
        """Calculates storage operations/sec, operations/min, and counter metrics."""
        now = time.time()
        cutoff_min = now - 60.0
        cutoff_sec = now - 1.0

        ops_in_last_min = sum(1 for t in self.metrics["ops_history"] if t >= cutoff_min)
        ops_in_last_sec = sum(1 for t in self.metrics["ops_history"] if t >= cutoff_sec)

        # Count monitored files in target directory
        monitored_file_count = 0
        total_storage_bytes = 0
        if self.target_dir.exists():
            for root, _, files in os.walk(self.target_dir):
                for f in files:
                    monitored_file_count += 1
                    try:
                        total_storage_bytes += os.path.getsize(os.path.join(root, f))
                    except OSError:
                        pass

        from backend.services.demo_manager import demo_manager
        current_session = demo_manager.get_current_session_id()

        return {
            "demo_session_id": current_session,
            "is_monitoring": self.is_running,
            "target_directory": str(self.target_dir),
            "files_created": self.metrics["created"],
            "files_modified": self.metrics["modified"],
            "files_deleted": self.metrics["deleted"],
            "files_renamed": self.metrics["renamed"],
            "suspicious_operations": self.metrics["suspicious"],
            "operations_per_second": ops_in_last_sec,
            "operations_per_minute": ops_in_last_min,
            "monitored_files_count": monitored_file_count,
            "monitored_storage_bytes": total_storage_bytes,
        }


# Global Storage Monitor singleton
storage_monitor = StorageMonitorService()

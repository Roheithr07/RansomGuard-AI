"""RansomGuard AI - Storage Telemetry API Router.

Exposes comprehensive storage volume utilization, real-time file operation counters,
directory structure overview, and storage configuration endpoints.
"""
import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.storage_monitor import storage_monitor
from backend.core.config import PROTECTED_DIRECTORY

router = APIRouter()


class StorageConfigRequest(BaseModel):
    directory_path: str


@router.get("/storage")
def get_storage_metrics():
    """Returns storage metrics, operation rates, and protected folder state."""
    metrics = storage_monitor.get_current_metrics()
    target_path = Path(metrics["target_directory"])

    # Disk usage statistics for the drive hosting the protected folder
    try:
        drive_path = str(target_path.anchor or "C:\\")
        disk_stat = shutil.disk_usage(drive_path)
        total_disk = disk_stat.total
        free_disk = disk_stat.free
        used_disk = disk_stat.used
        disk_percent = round((used_disk / total_disk) * 100, 1) if total_disk > 0 else 0.0
    except Exception:
        total_disk = 0
        used_disk = 0
        free_disk = 0
        disk_percent = 0.0

    # Monitored files list preview (sorted by most recently modified, up to 100 files)
    file_list = []
    total_bytes = 0
    from backend.core.config import SUSPICIOUS_EXTENSIONS
    if target_path.exists():
        for root, _, files in os.walk(target_path):
            for f in files:
                fp = Path(root) / f
                try:
                    st = fp.stat()
                    total_bytes += st.st_size
                    is_suspicious = fp.suffix.lower() in SUSPICIOUS_EXTENSIONS or ".locked" in f.lower()
                    file_list.append({
                        "name": f,
                        "path": str(fp.relative_to(target_path)).replace("\\", "/"),
                        "size_bytes": st.st_size,
                        "modified": st.st_mtime,
                        "extension": fp.suffix.lower() if fp.suffix else "none",
                        "status": "Flagged" if is_suspicious else "Clean"
                    })
                except OSError:
                    pass
        file_list.sort(key=lambda x: x["modified"], reverse=True)
        file_list = file_list[:100]

    monitored_files_count = len(file_list) if target_path.exists() else 0
    suspicious = metrics.get("suspicious_operations", 0)
    health_percentage = 100.0 if suspicious == 0 else max(0.0, round(100.0 - (suspicious * 5.0), 1))
    health_status = "Optimal" if suspicious == 0 else ("Warning" if suspicious < 3 else "Degraded")

    return {
        "protected_directory": str(target_path),
        "monitoring_active": storage_monitor.is_running,
        "storage_health_percentage": health_percentage,
        "storage_health_status": health_status,
        "disk_capacity_bytes": total_disk,
        "disk_used_bytes": used_disk,
        "disk_free_bytes": free_disk,
        "disk_used_percentage": disk_percent,
        "monitored_storage_bytes": total_bytes,
        "monitored_files_count": monitored_files_count,
        "files_created": metrics["files_created"],
        "files_modified": metrics["files_modified"],
        "files_deleted": metrics["files_deleted"],
        "files_renamed": metrics["files_renamed"],
        "operations_per_second": metrics["operations_per_second"],
        "operations_per_minute": metrics["operations_per_minute"],
        "suspicious_operations": metrics["suspicious_operations"],
        "recent_monitored_files": file_list,
    }


@router.post("/storage/configure")
def configure_storage(config: StorageConfigRequest):
    """Configures the active directory monitored by RansomGuard."""
    raw_path = config.directory_path.strip()
    if not raw_path:
        raise HTTPException(status_code=400, detail="Directory path cannot be empty.")

    # Reject invalid characters
    if any(char in raw_path for char in ['<', '>', '"', '|', '?', '*']):
        raise HTTPException(status_code=400, detail="Invalid characters detected in directory path.")

    try:
        new_dir = Path(raw_path).resolve()
        norm_path = str(new_dir).lower().rstrip("\\/")

        # Forbidden root and critical system directories
        forbidden = [
            "c:", "c:\\", "c:/", "c:\\windows", "c:/windows", "c:\\users", "c:/users",
            "c:\\program files", "c:/program files", "c:\\program files (x86)",
            "c:/program files (x86)", "/etc", "/var", "/usr", "/bin", "/sbin"
        ]
        if norm_path in forbidden or str(new_dir) == str(new_dir.anchor):
            raise HTTPException(status_code=400, detail="Configuring system root or OS directory directly is prohibited for safety.")

        if not new_dir.exists():
            new_dir.mkdir(parents=True, exist_ok=True)

        storage_monitor.stop()
        storage_monitor.target_dir = new_dir
        storage_monitor.metrics["created"] = 0
        storage_monitor.metrics["modified"] = 0
        storage_monitor.metrics["deleted"] = 0
        storage_monitor.metrics["renamed"] = 0
        storage_monitor.metrics["suspicious"] = 0
        storage_monitor.metrics["ops_history"] = []

        from backend.services.snapshot_manager import snapshot_manager
        from backend.services.recovery_manager import recovery_manager
        snapshot_manager.storage_dir = new_dir
        recovery_manager.target_dir = new_dir

        storage_monitor.start()

        from backend.core.database import get_db_connection
        from datetime import datetime, timezone
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO system_settings (key, value, updated_at)
            VALUES ('protected_directory', ?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
        """, (str(new_dir), datetime.now(timezone.utc).isoformat()))
        conn.commit()
        conn.close()

        from backend.services.audit_service import audit_service
        audit_service.log_event(
            event_type="storage_configuration_changed",
            action="Update Protected Storage Path",
            result="SUCCESS",
            severity="LOW",
            source="storage_service",
            related_entity_id=str(new_dir),
            details=f"Protected storage target path configured to {new_dir}"
        )

        return {
            "success": True,
            "new_directory": str(new_dir),
            "message": f"Protected storage directory updated and monitoring active on {new_dir}",
            "monitoring_active": storage_monitor.is_running,
            "metrics": storage_monitor.get_current_metrics()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot configure storage directory: {e}")





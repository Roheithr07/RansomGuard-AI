"""RansomGuard AI - Snapshot & Backup Manager Service.

Provides immutable local snapshot creation, SHA-256 cryptographic integrity verification,
manifest tracking in SQLite, and snapshot lifecycle management.
"""
import os
import shutil
import hashlib
import uuid
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from backend.core.config import PROTECTED_DIRECTORY, SNAPSHOT_DIRECTORY
from backend.core.database import get_db_connection
from backend.services.audit_service import audit_service

logger = logging.getLogger("ransomguard.snapshot")


class SnapshotManager:
    """Manages snapshot creation, file manifests, and integrity hashing."""

    def __init__(self, storage_dir: Optional[Path] = None, snapshots_dir: Optional[Path] = None):
        self.storage_dir = Path(storage_dir or PROTECTED_DIRECTORY).resolve()
        self.snapshots_dir = Path(snapshots_dir or SNAPSHOT_DIRECTORY).resolve()
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    @property
    def active_storage_dir(self) -> Path:
        """Returns the active monitored storage directory."""
        try:
            from backend.services.storage_monitor import storage_monitor
            if storage_monitor.target_dir and storage_monitor.target_dir.exists():
                return storage_monitor.target_dir
        except Exception:
            pass
        return self.storage_dir

    def calculate_file_sha256(self, file_path: Path) -> str:
        """Calculates SHA-256 hash for a specific file."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def create_snapshot(self, description: str = "Automated Storage Checkpoint") -> Dict[str, Any]:
        """Creates a snapshot copy of all files in protected storage with cryptographic manifests."""
        now = datetime.now(timezone.utc)
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        snapshot_id = f"snap_{timestamp_str}_{uuid.uuid4().hex[:6]}"
        snapshot_target_dir = self.snapshots_dir / snapshot_id
        snapshot_target_dir.mkdir(parents=True, exist_ok=True)

        file_manifests: List[Dict[str, Any]] = []
        total_size_bytes = 0
        file_count = 0
        overall_hasher = hashlib.sha256()

        source_dir = self.active_storage_dir
        if source_dir.exists():
            for root, _, files in os.walk(source_dir):
                for f in files:
                    src_file = Path(root) / f
                    if not src_file.is_file():
                        continue

                    rel_path = src_file.relative_to(source_dir)
                    dst_file = snapshot_target_dir / rel_path
                    dst_file.parent.mkdir(parents=True, exist_ok=True)

                    # Copy file preserving metadata
                    shutil.copy2(src_file, dst_file)

                    # Calculate hashes
                    file_hash = self.calculate_file_sha256(dst_file)
                    file_size = dst_file.stat().st_size
                    modified_at = datetime.fromtimestamp(dst_file.stat().st_mtime, timezone.utc).isoformat()

                    overall_hasher.update(file_hash.encode("utf-8"))
                    total_size_bytes += file_size
                    file_count += 1

                    file_manifests.append({
                        "relative_path": str(rel_path).replace("\\", "/"),
                        "file_size": file_size,
                        "sha256_hash": file_hash,
                        "modified_at": modified_at,
                    })

        integrity_hash = overall_hasher.hexdigest() if file_manifests else "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

        # Save manifest JSON inside snapshot directory as redundancy
        manifest_file = snapshot_target_dir / "manifest.json"
        with open(manifest_file, "w") as mf:
            json.dump({
                "snapshot_id": snapshot_id,
                "created_at": now.isoformat(),
                "file_count": file_count,
                "total_size_bytes": total_size_bytes,
                "integrity_hash": integrity_hash,
                "files": file_manifests
            }, mf, indent=2)

        # Store in SQLite
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO snapshots (
                    snapshot_id, created_at, file_count, total_size_bytes,
                    snapshot_path, integrity_hash, integrity_status,
                    description, recovery_available
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot_id,
                now.isoformat(),
                file_count,
                total_size_bytes,
                str(snapshot_target_dir),
                integrity_hash,
                "Valid",
                description,
                1
            ))

            for item in file_manifests:
                cursor.execute("""
                    INSERT INTO snapshot_files (
                        snapshot_id, relative_path, file_size,
                        sha256_hash, modified_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    snapshot_id,
                    item["relative_path"],
                    item["file_size"],
                    item["sha256_hash"],
                    item["modified_at"]
                ))

            conn.commit()
            logger.info("Snapshot %s created successfully with %d files (%d bytes)", snapshot_id, file_count, total_size_bytes)
            audit_service.log_event(
                event_type="snapshot_created",
                action="Create Immutable Snapshot",
                result="SUCCESS",
                severity="INFO",
                source="snapshot_manager",
                related_entity_id=snapshot_id,
                details=f"Created snapshot with {file_count} files ({total_size_bytes} bytes). Hash: {integrity_hash[:12]}..."
            )
        finally:
            conn.close()

        return {
            "snapshot_id": snapshot_id,
            "created_at": now.isoformat(),
            "file_count": file_count,
            "total_size_bytes": total_size_bytes,
            "snapshot_path": str(snapshot_target_dir),
            "integrity_hash": integrity_hash,
            "sha256_hash": integrity_hash,
            "integrity_status": "Valid",
            "description": description,
            "recovery_available": True
        }

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """Returns all snapshots ordered by creation date descending."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM snapshots ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "snapshot_id": r["snapshot_id"],
                "created_at": r["created_at"],
                "file_count": r["file_count"],
                "total_size_bytes": r["total_size_bytes"],
                "snapshot_path": r["snapshot_path"],
                "integrity_hash": r["integrity_hash"],
                "integrity_status": r["integrity_status"],
                "description": r["description"],
                "recovery_available": bool(r["recovery_available"]),
            })
        return results

    def verify_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """Performs cryptographic check on every file in the snapshot directory against manifest."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM snapshots WHERE snapshot_id = ?", (snapshot_id,))
        snapshot_row = cursor.fetchone()

        if not snapshot_row:
            conn.close()
            return {
                "snapshot_id": snapshot_id,
                "verified": False,
                "integrity_status": "NotFound",
                "checked_files": 0,
                "corrupted_files": [],
                "message": f"Snapshot {snapshot_id} does not exist"
            }

        cursor.execute("SELECT * FROM snapshot_files WHERE snapshot_id = ?", (snapshot_id,))
        files_rows = cursor.fetchall()

        snapshot_path = Path(snapshot_row["snapshot_path"])
        corrupted = []
        checked_count = 0

        for f in files_rows:
            rel = f["relative_path"]
            expected_hash = f["sha256_hash"]
            file_on_disk = snapshot_path / rel

            checked_count += 1
            if not file_on_disk.exists():
                corrupted.append(f"{rel} (missing)")
                continue

            try:
                actual_hash = self.calculate_file_sha256(file_on_disk)
                if actual_hash != expected_hash:
                    corrupted.append(f"{rel} (hash mismatch)")
            except Exception as e:
                corrupted.append(f"{rel} (read error: {e})")

        is_valid = len(corrupted) == 0
        status_str = "Valid" if is_valid else "Corrupted"

        cursor.execute("UPDATE snapshots SET integrity_status = ? WHERE snapshot_id = ?", (status_str, snapshot_id))
        conn.commit()
        conn.close()

        if is_valid:
            audit_service.log_event(
                event_type="snapshot_verified",
                action="Verify Snapshot Cryptographic Hash",
                result="VALID",
                severity="INFO",
                source="snapshot_manager",
                related_entity_id=snapshot_id,
                details=f"All {checked_count} snapshot files cryptographically verified against SHA-256 signatures."
            )
        else:
            audit_service.log_event(
                event_type="snapshot_corruption_detected",
                action="Verify Snapshot Cryptographic Hash",
                result="CORRUPTED",
                severity="CRITICAL",
                source="snapshot_manager",
                related_entity_id=snapshot_id,
                details=f"Integrity check failed: {len(corrupted)} corrupted files ({', '.join(corrupted[:3])})"
            )

        return {
            "snapshot_id": snapshot_id,
            "verified": is_valid,
            "integrity_status": status_str,
            "checked_files": checked_count,
            "corrupted_files": corrupted,
            "message": "All snapshot files verified successfully and matched SHA-256 signatures." if is_valid else f"Integrity check failed: {len(corrupted)} corrupted or altered files."
        }

    def delete_snapshot(self, snapshot_id: str) -> Tuple[bool, str]:
        """Deletes a snapshot and clears associated database manifest."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM snapshots WHERE snapshot_id = ?", (snapshot_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, f"Snapshot {snapshot_id} not found."

        path = Path(row["snapshot_path"])
        try:
            if path.exists():
                shutil.rmtree(path)
            cursor.execute("DELETE FROM snapshot_files WHERE snapshot_id = ?", (snapshot_id,))
            cursor.execute("DELETE FROM snapshots WHERE snapshot_id = ?", (snapshot_id,))
            conn.commit()
            audit_service.log_event(
                event_type="snapshot_deleted",
                action="Delete Snapshot Checkpoint",
                result="SUCCESS",
                severity="INFO",
                source="snapshot_manager",
                related_entity_id=snapshot_id,
                details=f"Snapshot {snapshot_id} removed from disk and database catalog"
            )
            return True, f"Snapshot {snapshot_id} deleted successfully."
        except Exception as e:
            conn.rollback()
            return False, f"Failed to delete snapshot: {e}"
        finally:
            conn.close()


# Global Snapshot Manager singleton
snapshot_manager = SnapshotManager()

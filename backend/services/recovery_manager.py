"""RansomGuard AI - Safe Storage Recovery Manager Service.

Performs verified restorations from immutable snapshots back into the protected storage directory.
Ensures pre-restoration integrity checks, atomic rollback protection, and audit logging.
"""
import os
import shutil
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from backend.core.config import PROTECTED_DIRECTORY
from backend.core.database import get_db_connection
from backend.services.snapshot_manager import snapshot_manager
from backend.services.audit_service import audit_service

logger = logging.getLogger("ransomguard.recovery")


class RecoveryManager:
    """Manages restoration workflows, preview generations, and audit logging."""

    def __init__(self, target_storage_dir: Optional[Path] = None):
        self.target_dir = Path(target_storage_dir or PROTECTED_DIRECTORY).resolve()

    @property
    def active_target_dir(self) -> Path:
        """Returns the active monitored storage directory for recovery."""
        try:
            from backend.services.storage_monitor import storage_monitor
            if storage_monitor.target_dir and storage_monitor.target_dir.exists():
                return storage_monitor.target_dir
        except Exception:
            pass
        return self.target_dir

    def preview_recovery(self, snapshot_id: str) -> Dict[str, Any]:
        """Provides a safe dry-run preview of files that would be restored."""
        self.target_dir = self.active_target_dir
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM snapshots WHERE snapshot_id = ?", (snapshot_id,))
        snap = cursor.fetchone()

        if not snap:
            conn.close()
            raise ValueError(f"Snapshot '{snapshot_id}' does not exist.")

        cursor.execute("SELECT relative_path, file_size FROM snapshot_files WHERE snapshot_id = ?", (snapshot_id,))
        file_rows = cursor.fetchall()
        conn.close()

        files_list = [r["relative_path"] for r in file_rows]
        integrity_check = snapshot_manager.verify_snapshot(snapshot_id)

        return {
            "snapshot_id": snapshot_id,
            "file_count": snap["file_count"],
            "total_size_bytes": snap["total_size_bytes"],
            "integrity_valid": integrity_check["verified"],
            "files_to_restore": files_list,
            "warning": None if integrity_check["verified"] else "Snapshot failed integrity verification. Restoration may restore corrupted data."
        }

    def restore_snapshot(self, snapshot_id: str, confirmation: bool = True) -> Dict[str, Any]:
        """Restores files from a verified snapshot to protected storage with safety checkpoints and post-restore verification."""
        if not confirmation:
            raise ValueError("Recovery requires explicit confirmation.")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM snapshots WHERE snapshot_id = ?", (snapshot_id,))
        snap = cursor.fetchone()

        if not snap:
            conn.close()
            raise FileNotFoundError(f"Snapshot '{snapshot_id}' not found.")

        # Step 1: Confirm snapshot integrity_status == 'Valid'
        if snap["integrity_status"] != "Valid":
            conn.close()
            raise ValueError(f"Snapshot '{snapshot_id}' integrity status is '{snap['integrity_status']}'. Only 'Valid' snapshots can be restored.")

        snapshot_dir = Path(snap["snapshot_path"])
        if not snapshot_dir.exists():
            conn.close()
            raise FileNotFoundError(f"Snapshot storage directory {snapshot_dir} does not exist on disk.")

        # Step 2: Cryptographic pre-flight integrity verification before restore
        verification = snapshot_manager.verify_snapshot(snapshot_id)
        if not verification["verified"]:
            conn.close()
            raise ValueError(f"Pre-restore integrity check failed for '{snapshot_id}': {verification.get('message', 'Corrupted file hashes detected')}")

        # Step 3: Ensure protected storage directory exists
        self.target_dir = self.active_target_dir
        self.target_dir.mkdir(parents=True, exist_ok=True)

        # Step 4: Create PRE-RESTORE safety snapshot of CURRENT protected storage
        try:
            safety_snap = snapshot_manager.create_snapshot(description="Automatic pre-restore safety checkpoint")
            safety_snapshot_id = safety_snap["snapshot_id"]
            logger.info("Created pre-restore safety snapshot %s before restoring %s", safety_snapshot_id, snapshot_id)
        except Exception as e:
            conn.close()
            logger.error("Failed to create pre-restore safety snapshot: %s", e)
            raise RuntimeError(f"Failed to create pre-restore safety snapshot: {e}")

        recovery_id = f"rec-{uuid.uuid4().hex[:10]}"
        started_at = datetime.now(timezone.utc).isoformat()

        # Step 5: Record operation started
        cursor.execute("""
            INSERT INTO recovery_operations (
                recovery_id, snapshot_id, safety_snapshot_id, target_directory,
                started_at, status, details, verification_result
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            recovery_id,
            snapshot_id,
            safety_snapshot_id,
            str(self.target_dir),
            started_at,
            "IN_PROGRESS",
            f"Restoring {snap['file_count']} files from snapshot {snapshot_id} (Safety checkpoint: {safety_snapshot_id})",
            "PENDING"
        ))
        conn.commit()

        audit_service.log_event(
            event_type="recovery_started",
            action="Initiate Storage Restoration",
            result="IN_PROGRESS",
            severity="WARNING",
            source="recovery_manager",
            related_entity_id=recovery_id,
            details=f"Starting restore of {snap['file_count']} files from {snapshot_id}. Pre-restore checkpoint: {safety_snapshot_id}"
        )

        # Step 6: Perform restore
        restored_count = 0
        restored_bytes = 0

        try:
            cursor.execute("SELECT relative_path, file_size, sha256_hash FROM snapshot_files WHERE snapshot_id = ?", (snapshot_id,))
            files_to_restore = cursor.fetchall()

            for item in files_to_restore:
                rel = item["relative_path"]
                # Safety rule: Do not restore manifest.json into protected storage
                if rel.lower() == "manifest.json" or rel.lower().endswith("/manifest.json"):
                    continue

                src = snapshot_dir / rel
                dst = self.target_dir / rel

                if src.exists() and src.is_file():
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    restored_count += 1
                    restored_bytes += item["file_size"]
                else:
                    raise FileNotFoundError(f"Snapshot source file {src} is missing from disk.")

            # Step 7: Post-restore cryptographic SHA-256 verification
            post_verify_mismatches = []
            for item in files_to_restore:
                rel = item["relative_path"]
                if rel.lower() == "manifest.json" or rel.lower().endswith("/manifest.json"):
                    continue
                dst = self.target_dir / rel
                if not dst.exists():
                    post_verify_mismatches.append(f"{rel}: file not found after restore")
                    continue
                actual_hash = snapshot_manager.calculate_file_sha256(dst)
                if actual_hash != item["sha256_hash"]:
                    post_verify_mismatches.append(f"{rel}: hash mismatch (expected {item['sha256_hash'][:8]}, got {actual_hash[:8]})")
                if dst.stat().st_size != item["file_size"]:
                    post_verify_mismatches.append(f"{rel}: size mismatch (expected {item['file_size']}, got {dst.stat().st_size})")

            if post_verify_mismatches:
                # Post-restore verification failed! Attempt rollback to safety snapshot
                rollback_ok = False
                try:
                    safety_dir = Path(snapshot_manager.snapshots_dir) / safety_snapshot_id
                    cursor.execute("SELECT relative_path FROM snapshot_files WHERE snapshot_id = ?", (safety_snapshot_id,))
                    safety_files = cursor.fetchall()
                    for sf in safety_files:
                        s_rel = sf["relative_path"]
                        s_src = safety_dir / s_rel
                        s_dst = self.target_dir / s_rel
                        if s_src.exists() and s_src.is_file():
                            s_dst.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(s_src, s_dst)
                    rollback_ok = True
                except Exception as rb_err:
                    logger.error("Failed to rollback to safety snapshot %s: %s", safety_snapshot_id, rb_err)

                completed_at = datetime.now(timezone.utc).isoformat()
                final_status = "ROLLED_BACK" if rollback_ok else "FAILED"
                err_detail = f"Post-restore cryptographic verification failed: {'; '.join(post_verify_mismatches)}"
                cursor.execute("""
                    UPDATE recovery_operations SET
                        completed_at = ?,
                        status = ?,
                        verification_result = 'HASH_MISMATCH',
                        error_message = ?,
                        details = ?
                    WHERE recovery_id = ?
                """, (
                    completed_at,
                    final_status,
                    err_detail,
                    f"Rolled back to safety checkpoint {safety_snapshot_id}" if rollback_ok else "Rollback failed",
                    recovery_id
                ))
                conn.commit()

                audit_service.log_event(
                    event_type="recovery_rolled_back" if rollback_ok else "recovery_failed",
                    action="Disaster Recovery Rollback",
                    result=final_status,
                    severity="CRITICAL",
                    source="recovery_manager",
                    related_entity_id=recovery_id,
                    details=f"Post-restore check failed: {err_detail}. Rollback: {final_status}"
                )
                raise ValueError(err_detail)

            # Step 8: Mark SUCCESS
            completed_at = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
                UPDATE recovery_operations SET
                    completed_at = ?,
                    status = 'SUCCESS',
                    restored_files_count = ?,
                    restored_bytes = ?,
                    verification_result = 'VERIFIED_MATCH',
                    details = ?
                WHERE recovery_id = ?
            """, (
                completed_at,
                restored_count,
                restored_bytes,
                f"Successfully restored and verified {restored_count} files ({restored_bytes} bytes). Safety checkpoint: {safety_snapshot_id}",
                recovery_id
            ))
            conn.commit()

            audit_service.log_event(
                event_type="recovery_completed",
                action="Complete Storage Restoration",
                result="SUCCESS",
                severity="INFO",
                source="recovery_manager",
                related_entity_id=recovery_id,
                details=f"Successfully restored and verified {restored_count} files ({restored_bytes} bytes) from {snapshot_id}. Safety checkpoint: {safety_snapshot_id}"
            )

            logger.info(
                "Recovery %s succeeded: %d files verified in %s (Safety: %s)",
                recovery_id, restored_count, self.target_dir, safety_snapshot_id
            )

            return {
                "success": True,
                "recovery_id": recovery_id,
                "snapshot_id": snapshot_id,
                "safety_snapshot_id": safety_snapshot_id,
                "status": "SUCCESS",
                "restored_files_count": restored_count,
                "restored_bytes": restored_bytes,
                "verification_result": "VERIFIED_MATCH",
                "integrity_verification": "VERIFIED_MATCH",
                "started_at": started_at,
                "completed_at": completed_at,
                "message": f"Recovery completed successfully. {restored_count} files verified and restored.",
                "details": f"Safety checkpoint {safety_snapshot_id} created prior to restoration."
            }

        except Exception as e:
            if not isinstance(e, ValueError):
                completed_at = datetime.now(timezone.utc).isoformat()
                cursor.execute("""
                    UPDATE recovery_operations SET
                        completed_at = ?,
                        status = 'FAILED',
                        verification_result = 'FAILED',
                        error_message = ?
                    WHERE recovery_id = ?
                """, (completed_at, str(e), recovery_id))
                conn.commit()

                audit_service.log_event(
                    event_type="recovery_failed",
                    action="Execute Storage Restoration",
                    result="FAILED",
                    severity="CRITICAL",
                    source="recovery_manager",
                    related_entity_id=recovery_id,
                    details=f"Restoration failed: {e}"
                )
                logger.error("Recovery failed: %s", e)
            raise
        finally:
            conn.close()

    def get_recovery_history(self) -> List[Dict[str, Any]]:
        """Retrieves past recovery audit log entries."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recovery_operations ORDER BY id DESC LIMIT 50")
        rows = cursor.fetchall()
        conn.close()

        return [dict(r) for r in rows]


# Global Recovery Manager singleton
recovery_manager = RecoveryManager()

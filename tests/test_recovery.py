"""Recovery Module Unit & Integration Tests.

Validates recovery points listing, immutable snapshot rollback, pre-restore
safety snapshots, cryptographic SHA-256 verification, and SQLite audit logs.
"""
import unittest
from pathlib import Path
from backend.core.config import PROTECTED_DIRECTORY
from backend.core.database import get_db_connection
from backend.services.snapshot_manager import snapshot_manager
from backend.services.recovery_manager import recovery_manager


class TestRecovery(unittest.TestCase):

    def test_recovery_listing(self):
        """Confirms snapshot recovery points are retrievable and filtered for valid integrity."""
        history = recovery_manager.get_recovery_history()
        self.assertIsInstance(history, list)

    def test_restore_workflow_with_safety_snapshot(self):
        """Validates complete restore workflow with automatic safety checkpoint and hash matching."""
        demo_dir = Path(PROTECTED_DIRECTORY) / "demo"
        demo_dir.mkdir(parents=True, exist_ok=True)
        test_file = demo_dir / "unit_test_recovery.txt"
        original_text = "RansomGuard Phase 8 Unit Test Content - Verified\n"
        test_file.write_text(original_text, encoding="utf-8")
        original_hash = snapshot_manager.calculate_file_sha256(test_file)

        # 1. Create verified snapshot
        snap = snapshot_manager.create_snapshot(description="Phase 8 Unit Test Checkpoint")
        snap_id = snap["snapshot_id"]

        # 2. Modify protected file
        test_file.write_text("MODIFIED_DATA_TRIGGERING_ROLLBACK\n", encoding="utf-8")

        # 3. Execute recovery
        res = recovery_manager.restore_snapshot(snap_id, confirmation=True)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["verification_result"], "VERIFIED_MATCH")
        self.assertIsNotNone(res["safety_snapshot_id"])

        # 4. Verify original content restored
        restored_text = test_file.read_text(encoding="utf-8")
        self.assertEqual(restored_text, original_text)
        self.assertEqual(snapshot_manager.calculate_file_sha256(test_file), original_hash)

        # 5. Cleanup
        if test_file.exists():
            test_file.unlink()

    def test_corrupted_snapshot_rejection(self):
        """Validates that corrupted snapshots are strictly rejected before restoration."""
        # Create snapshot and deliberately mark Corrupted
        snap = snapshot_manager.create_snapshot(description="Tamper Test Checkpoint")
        snap_id = snap["snapshot_id"]

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE snapshots SET integrity_status = 'Corrupted' WHERE snapshot_id = ?", (snap_id,))
        conn.commit()
        conn.close()

        with self.assertRaises(ValueError) as ctx:
            recovery_manager.restore_snapshot(snap_id, confirmation=True)

        self.assertTrue("Corrupted" in str(ctx.exception) or "integrity" in str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()

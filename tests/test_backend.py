"""RansomGuard AI - Comprehensive Verification Test Suite.

Tests database schemas, watchdog monitor initialization, risk engine,
cryptographic snapshots, safe disaster recovery, and API endpoints.
"""
import os
import sys
import json
import unittest
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.core.config import PROTECTED_DIRECTORY, SNAPSHOT_DIRECTORY, DATABASE_PATH
from backend.core.database import init_database, get_db_connection
from backend.services.risk_engine import risk_engine
from backend.services.snapshot_manager import snapshot_manager
from backend.services.recovery_manager import recovery_manager
from backend.services.simulator import safe_simulator
from backend.services.storage_monitor import storage_monitor
from backend.main import app


class TestRansomGuardBackend(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initializes database and testing environment."""
        init_database()

    def test_database_initialization(self):
        """Ensures all required SQLite tables and indexes exist."""
        conn = get_db_connection()
        cursor = conn.cursor()

        tables = ["events", "threats", "snapshots", "snapshot_files", "recovery_operations", "system_settings", "audit_logs"]
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            row = cursor.fetchone()
            self.assertIsNotNone(row, f"Table '{table}' should exist in database.")

        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_events_timestamp'")
        self.assertIsNotNone(cursor.fetchone(), "Index idx_events_timestamp should exist.")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_audit_timestamp'")
        self.assertIsNotNone(cursor.fetchone(), "Index idx_audit_timestamp should exist.")
        conn.close()

    def test_entropy_calculation(self):
        """Verifies Shannon entropy logic on low vs high randomness files."""
        test_file = PROTECTED_DIRECTORY / "entropy_test.txt"
        with open(test_file, "w") as f:
            f.write("A" * 1000)  # Low entropy repeated character

        low_entropy = risk_engine.calculate_entropy(str(test_file))
        self.assertLess(low_entropy, 1.0, "Repeated character file must have low entropy.")

        # High entropy random bytes
        with open(test_file, "wb") as f:
            f.write(os.urandom(2048))

        high_entropy = risk_engine.calculate_entropy(str(test_file))
        self.assertGreater(high_entropy, 7.0, "Random byte file must have high entropy (>7.0).")

        if test_file.exists():
            test_file.unlink()

    def test_risk_scoring_detection(self):
        """Tests that suspicious ransomware extensions and high entropy elevate the risk score."""
        eval_result = risk_engine.evaluate_event(
            event_type="renamed",
            file_path="protected_storage/accounting.xlsx.locked",
            entropy=7.8,
            old_path="protected_storage/accounting.xlsx"
        )

        self.assertGreaterEqual(eval_result["risk_score"], 60, "Ransomware extension + high entropy must trigger HIGH or CRITICAL score.")
        self.assertIn(eval_result["severity"], ["HIGH", "CRITICAL"])
        self.assertTrue(len(eval_result["reasons"]) > 0)

    def test_snapshot_creation_and_verification(self):
        """Tests local immutable snapshot creation and cryptographic SHA-256 validation."""
        # Create a sample document in protected storage
        doc_path = PROTECTED_DIRECTORY / "sample_doc.txt"
        with open(doc_path, "w") as f:
            f.write("Integrity test content for snapshot verification.")

        snapshot = snapshot_manager.create_snapshot(description="Test Verification Snapshot")
        self.assertIsNotNone(snapshot["snapshot_id"])
        self.assertTrue(snapshot["recovery_available"])

        # Cryptographically verify the snapshot
        verification = snapshot_manager.verify_snapshot(snapshot["snapshot_id"])
        self.assertTrue(verification["verified"], "Freshly created snapshot must pass SHA-256 verification.")
        self.assertEqual(verification["integrity_status"], "Valid")

        # Test recovery preview
        preview = recovery_manager.preview_recovery(snapshot["snapshot_id"])
        self.assertTrue(preview["integrity_valid"])
        self.assertIn("sample_doc.txt", [Path(p).name for p in preview["files_to_restore"]])

        # Clean up test file
        if doc_path.exists():
            doc_path.unlink()

    def test_safe_simulator(self):
        """Ensures simulation operates safely inside protected_storage/demo/ without touching parent files."""
        result = safe_simulator.run_simulation(intensity="low")
        self.assertTrue(result["success"])
        self.assertEqual(result["sandbox_directory"], str(PROTECTED_DIRECTORY / "demo"))

        # Clean up demo files
        cleanup = safe_simulator.cleanup_demo_folder()
        self.assertTrue(cleanup["success"])

    def test_fastapi_routes_registered(self):
        """Verifies that all required API endpoints are mounted on the FastAPI app."""
        openapi_paths = set(app.openapi()["paths"].keys())
        ws_routes = {route.path for route in app.routes if hasattr(route, "path")}
        routes = openapi_paths.union(ws_routes)
        expected_endpoints = [
            "/api/dashboard",
            "/api/storage",
            "/api/events",
            "/api/threats",
            "/api/snapshots",
            "/api/recovery",
            "/api/ai-analysis",
            "/api/reports",
            "/api/monitor/start",
            "/api/monitor/stop",
            "/api/demo/simulate",
            "/api/system/status",
            "/ws/monitor",
            "/docs",
        ]
        for ep in expected_endpoints:
            self.assertIn(ep, routes, f"Endpoint '{ep}' must be registered on FastAPI app.")

    def test_security_reports_and_audit(self):
        """Verifies Phase 10 security reports, persistent audit logs, and export."""
        from backend.api.reports import get_security_report, export_security_report
        from backend.services.audit_service import audit_service

        # 1. Audit logging persistence
        audit_entry = audit_service.log_event(
            event_type="test_event",
            action="Test Security Action",
            result="SUCCESS",
            severity="INFO",
            source="test_suite",
            details="Testing persistent audit logs"
        )
        self.assertIsNotNone(audit_entry["audit_id"])

        logs = audit_service.get_audit_logs(limit=10)
        self.assertGreater(logs["total"], 0)
        self.assertTrue(any(l["audit_id"] == audit_entry["audit_id"] for l in logs["logs"]))

        # 2. Security report structure
        report = get_security_report()
        self.assertIn("executive_summary", report)
        self.assertIn("events", report)
        self.assertIn("threats", report)
        self.assertIn("snapshots", report)
        self.assertIn("recovery", report)
        self.assertIn("ai_analysis", report)
        self.assertIn("storage", report)
        self.assertIn("recommendations", report)
        self.assertIn("compliance_evidence", report)
        self.assertIn("latest_activity", report)

        # 3. Export
        export_resp = export_security_report()
        self.assertEqual(export_resp.status_code, 200)
        exported_data = json.loads(export_resp.body.decode("utf-8"))
        self.assertIn("audit_history", exported_data)


if __name__ == "__main__":
    unittest.main()

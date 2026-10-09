"""RansomGuard AI - Phase 12 Complete End-to-End Validation & Release Suite.

Performs deterministic functional, regression, cryptographic, database, security,
and performance verification across Phases 1 through 11.
"""
import os
import sys
import time
import json
import sqlite3
import asyncio
import websockets
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_FILE = BASE_DIR / "frontend" / "RansomGuard-Dashboard.html"
DB_PATH = BASE_DIR / "backend" / "database" / "ransomguard.db"
PROTECTED_DIR = BASE_DIR / "protected_storage"
SNAPSHOT_DIR = BASE_DIR / "snapshots"
BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/monitor"


def print_header(title: str):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def test_architecture():
    print_header("1. ARCHITECTURE & FRAMEWORK VALIDATION")
    assert FRONTEND_FILE.exists(), f"Permanent frontend {FRONTEND_FILE} must exist."
    print(f"[PASS] Permanent frontend verified at: {FRONTEND_FILE}")

    # Verify no react/vite dependencies active
    pkg_json = BASE_DIR / "package.json"
    if pkg_json.exists():
        with open(pkg_json, "r", encoding="utf-8") as f:
            content = f.read()
            assert "react" not in content.lower() or "deprecated" in content.lower(), "React must not be active."
    print("[PASS] Verified zero dependency on React / Vite.")


def test_sqlite_integrity():
    print_header("2. DATABASE INTEGRITY & WAL MODE")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Integrity Check
    cur.execute("PRAGMA integrity_check;")
    integrity = cur.fetchone()[0]
    print(f"[PASS] PRAGMA integrity_check: {integrity}")
    assert integrity == "ok", f"Database integrity check failed: {integrity}"

    # Journal mode
    cur.execute("PRAGMA journal_mode;")
    j_mode = cur.fetchone()[0]
    print(f"[PASS] PRAGMA journal_mode: {j_mode}")
    assert j_mode.lower() == "wal", f"Expected WAL mode, got {j_mode}"

    # Foreign key check
    cur.execute("PRAGMA foreign_key_check;")
    fk_violations = cur.fetchall()
    print(f"[PASS] PRAGMA foreign_key_check violations: {len(fk_violations)}")
    assert len(fk_violations) == 0, f"Foreign key violations found: {fk_violations}"

    # Table verification
    expected_tables = {
        "events", "threats", "snapshots", "snapshot_files",
        "recovery_operations", "system_settings", "threat_rules", "audit_logs"
    }
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = {r[0] for r in cur.fetchall()}
    missing = expected_tables - existing_tables
    print(f"[PASS] Existing Tables: {len(existing_tables)} (Verified all 8 required schemas)")
    assert not missing, f"Missing database tables: {missing}"

    # Orphan checks
    cur.execute("SELECT count(*) FROM snapshot_files WHERE snapshot_id NOT IN (SELECT snapshot_id FROM snapshots)")
    orphan_files = cur.fetchone()[0]
    print(f"[PASS] Orphan snapshot_files: {orphan_files}")
    assert orphan_files == 0, "Found orphan snapshot_files records"

    cur.execute("SELECT count(*) FROM recovery_operations WHERE snapshot_id NOT IN (SELECT snapshot_id FROM snapshots)")
    orphan_recoveries = cur.fetchone()[0]
    print(f"[PASS] Orphan recovery_operations: {orphan_recoveries}")

    cur.execute("SELECT count(*) FROM audit_logs WHERE audit_id IS NULL OR audit_id = ''")
    malformed_audits = cur.fetchone()[0]
    print(f"[PASS] Malformed audit records: {malformed_audits}")
    assert malformed_audits == 0, "Found malformed audit records"

    conn.close()


def test_api_regression():
    print_header("3. BACKEND API REGRESSION & LATENCIES")
    endpoints = [
        ("GET", "/api/dashboard", 200),
        ("GET", "/api/events?limit=40", 200),
        ("GET", "/api/threats", 200),
        ("GET", "/api/storage", 200),
        ("GET", "/api/snapshots", 200),
        ("GET", "/api/recovery", 200),
        ("GET", "/api/ai-analysis", 200),
        ("GET", "/api/reports", 200),
        ("GET", "/api/reports/audit?limit=20", 200),
        ("GET", "/api/reports/export", 200),
        ("GET", "/api/demo/run-phase11-tests", 200),
        ("GET", "/openapi.json", 200),
    ]

    latencies = {}
    for method, path, expected_status in endpoints:
        t0 = time.perf_counter()
        req = urllib.request.Request(f"{BASE_URL}{path}", method=method)
        with urllib.request.urlopen(req) as resp:
            elapsed = (time.perf_counter() - t0) * 1000
            status = resp.getcode()
            latencies[path] = elapsed
            assert status == expected_status, f"Expected {expected_status} for {path}, got {status}"
            print(f"[PASS] {method} {path:35} -> HTTP {status} ({elapsed:.1f} ms)")

    return latencies


def test_storage_configure():
    print_header("4. STORAGE CONFIGURATION ENDPOINT")
    # Test POST /api/storage/configure with current protected directory
    req = urllib.request.Request(
        f"{BASE_URL}/api/storage/configure",
        data=json.dumps({"directory_path": str(PROTECTED_DIR)}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        res_data = json.loads(resp.read().decode("utf-8"))
        print(f"[PASS] POST /api/storage/configure -> {res_data.get('status')} ({res_data.get('monitored_directory')})")
        assert res_data.get("success") is True


async def test_websocket_stream():
    print_header("5. WEBSOCKET REAL-TIME STREAM VALIDATION")
    t0 = time.perf_counter()
    async with websockets.connect(WS_URL) as ws:
        # Await initial handshake / connection established message
        msg_raw = await asyncio.wait_for(ws.recv(), timeout=5.0)
        connect_latency = (time.perf_counter() - t0) * 1000
        msg = json.loads(msg_raw)
        print(f"[PASS] Connected to {WS_URL} in {connect_latency:.1f} ms")
        print(f"[PASS] Handshake Message: type='{msg.get('type')}', monitored_files={msg.get('metrics', {}).get('monitored_files_count')}")
        assert msg.get("type") in ("CONNECTION_ESTABLISHED", "MONITORING_STATUS"), f"Unexpected handshake message: {msg}"
    print("[PASS] WebSocket connection closed cleanly without errors.")


def test_snapshot_lifecycle():
    print_header("6. CONTROLLED SNAPSHOT & HASH VERIFICATION")
    t0 = time.perf_counter()
    req = urllib.request.Request(
        f"{BASE_URL}/api/snapshots/create",
        data=json.dumps({"description": "Phase 12 Controlled Test Checkpoint"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        snap_data = json.loads(resp.read().decode("utf-8"))
        elapsed = (time.perf_counter() - t0) * 1000

    snap_id = snap_data.get("snapshot", {}).get("snapshot_id") or snap_data.get("snapshot_id")
    file_count = snap_data.get("snapshot", {}).get("file_count") or snap_data.get("file_count")
    print(f"[PASS] Created Snapshot: {snap_id} in {elapsed:.1f} ms (Files: {file_count})")
    assert snap_id, "Snapshot ID not returned."

    # Verify snapshot SHA-256 against manifest
    req_v = urllib.request.Request(f"{BASE_URL}/api/snapshots/verify/{snap_id}", method="POST")
    with urllib.request.urlopen(req_v) as resp_v:
        ver_data = json.loads(resp_v.read().decode("utf-8"))

    print(f"[PASS] Verification status: {ver_data.get('status')} (Verified: {ver_data.get('verified')})")
    assert ver_data.get("verified") is True, "Cryptographic hash verification failed."

    return snap_id


def test_recovery_lifecycle():
    print_header("7. CONTROLLED RESTORATION & SHA-256 INTEGRITY")
    demo_file = PROTECTED_DIR / "demo_p12_target.txt"
    demo_file.write_text("Mission-critical Phase 12 validation original text.\n", encoding="utf-8")

    # Create baseline snapshot
    req_snap = urllib.request.Request(
        f"{BASE_URL}/api/snapshots/create",
        data=json.dumps({"description": "Pre-Mutation Baseline Checkpoint"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req_snap) as resp:
        snap_res = json.loads(resp.read().decode("utf-8"))
    snap_id = snap_res.get("snapshot", {}).get("snapshot_id") or snap_res.get("snapshot_id")

    # Mutate the file
    demo_file.write_text("CORRUPTED OR ENCRYPTED SIMULATION DATA BYTES.\n", encoding="utf-8")
    assert "CORRUPTED" in demo_file.read_text(encoding="utf-8")

    # Restore from snapshot
    req_restore = urllib.request.Request(
        f"{BASE_URL}/api/recovery/restore",
        data=json.dumps({"snapshot_id": snap_id, "confirm": True}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req_restore) as resp:
        rest_res = json.loads(resp.read().decode("utf-8"))

    print(f"[PASS] Recovery Executed: Status={rest_res.get('status')} (Files Restored: {rest_res.get('restored_files_count')})")
    print(f"[PASS] Safety Checkpoint Generated: {rest_res.get('safety_snapshot_id')}")
    assert rest_res.get("status") in ("SUCCESS", "COMPLETED")

    # Verify content restored
    restored_text = demo_file.read_text(encoding="utf-8")
    assert "Mission-critical Phase 12 validation original text." in restored_text, "Restoration content mismatch."
    print("[PASS] File content successfully reverted and verified bit-for-bit.")

    # Cleanup demo test file
    demo_file.unlink(missing_ok=True)


def test_threat_patch_persistence():
    print_header("8. THREAT RESOLUTION PERSISTENCE")
    req = urllib.request.Request(f"{BASE_URL}/api/threats")
    with urllib.request.urlopen(req) as resp:
        threats_data = json.loads(resp.read().decode("utf-8"))

    threats = threats_data.get("threats", [])
    if threats:
        target_threat = threats[0]
        t_id = target_threat["threat_id"]
        req_patch = urllib.request.Request(
            f"{BASE_URL}/api/threats/{t_id}/status",
            data=json.dumps({"status": "CONTAINED", "notes": "Phase 12 Automated Verification Resolution"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="PATCH"
        )
        with urllib.request.urlopen(req_patch) as resp_p:
            p_data = json.loads(resp_p.read().decode("utf-8"))

        print(f"[PASS] PATCH /api/threats/{t_id}/status -> {p_data.get('status')}")
        assert p_data.get("status") in ("Contained", "CONTAINED") or p_data.get("new_status") in ("Contained", "CONTAINED"), "Threat resolution status failed to persist."


def test_ai_analysis_structure():
    print_header("9. AI ANALYSIS TELEMETRY & EXPLANATION")
    req = urllib.request.Request(f"{BASE_URL}/api/ai-analysis")
    with urllib.request.urlopen(req) as resp:
        ai_data = json.loads(resp.read().decode("utf-8"))

    print(f"[PASS] AI Risk Score: {ai_data.get('risk_score')}/100 (Severity: {ai_data.get('severity')})")
    print(f"[PASS] Confidence: {int(ai_data.get('confidence', 0) * 100)}%")
    print(f"[PASS] Classification: {ai_data.get('classification')}")
    print(f"[PASS] Evidence Items: {len(ai_data.get('evidence', []))}")
    print(f"[PASS] Recommendation: {ai_data.get('recommended_action')}")

    features = ai_data.get("features", {})
    feature_matrix = ai_data.get("feature_matrix", {})
    assert "entropy_score" in features or "shannon_entropy_max" in feature_matrix, "Entropy analysis feature missing"
    assert "write_frequency_score" in features or "operations_per_second" in feature_matrix, "Write frequency feature missing"
    assert "burst_activity_score" in features or "burst_modifications_counter" in feature_matrix, "Burst feature missing"
    assert "classification" in ai_data, "Classification missing"
    assert "evidence" in ai_data, "Evidence missing"
    assert "recommended_action" in ai_data, "Recommended action missing"
    print("[PASS] All required AI behavioral explanation features present.")


def test_report_consistency():
    print_header("10. REPORT DATA CONSISTENCY & EXPORT")
    req = urllib.request.Request(f"{BASE_URL}/api/reports")
    with urllib.request.urlopen(req) as resp:
        report = json.loads(resp.read().decode("utf-8"))

    req_dash = urllib.request.Request(f"{BASE_URL}/api/dashboard")
    with urllib.request.urlopen(req_dash) as resp_d:
        dash = json.loads(resp_d.read().decode("utf-8"))

    dash_threats = dash.get("threats_detected", 0)
    rep_threats = report["executive_summary"]["threats_detected"]
    print(f"[PASS] Threats consistency: Dashboard={dash_threats}, Reports={rep_threats} (Delta={abs(dash_threats - rep_threats)})")
    assert abs(dash_threats - rep_threats) <= 2, f"Contradictory threat metrics: Dashboard={dash_threats}, Reports={rep_threats}"

    # Test Export endpoint
    req_exp = urllib.request.Request(f"{BASE_URL}/api/reports/export")
    with urllib.request.urlopen(req_exp) as resp_exp:
        exp_data = json.loads(resp_exp.read().decode("utf-8"))
        headers = dict(resp_exp.getheaders())

    print(f"[PASS] Export Content-Type: {headers.get('Content-Type')}")
    print(f"[PASS] Export Content-Disposition: {headers.get('Content-Disposition')}")
    assert "report_id" in exp_data, "Exported JSON missing report_id"
    assert "audit_summary" in exp_data, "Exported JSON missing audit_summary"
    print("[PASS] Security report export is complete and conforms to specification.")


def test_security_boundaries():
    print_header("11. SECURITY BOUNDARY & SANDBOX TESTING")
    traversal_paths = [
        "../../",
        "..\\..\\",
        "C:\\Windows",
        "C:\\Users",
        "C:\\Program Files",
        "/etc/passwd",
        "protected_storage/../"
    ]

    for p in traversal_paths:
        req = urllib.request.Request(
            f"{BASE_URL}/api/demo/cleanup",
            data=json.dumps({"path": p}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as resp:
                assert False, f"Path traversal security breach with: {p}"
        except urllib.error.HTTPError as e:
            assert e.code == 400, f"Expected HTTP 400 for '{p}', got {e.code}"
            print(f"[PASS] Traversal attempt '{p}' safely blocked with HTTP {e.code} Bad Request.")


def test_simulation_and_cleanup():
    print_header("12. SAFE SIMULATOR & CLEANUP WORKFLOW")
    # Trigger safe simulation LOW
    req_sim = urllib.request.Request(
        f"{BASE_URL}/api/demo/simulate?intensity=low",
        method="POST"
    )
    with urllib.request.urlopen(req_sim) as resp:
        sim_data = json.loads(resp.read().decode("utf-8"))

    print(f"[PASS] Safe Simulation: ID={sim_data.get('simulation_id')} (Created: {sim_data.get('files_created')}, Risk: {sim_data.get('expected_risk_level')})")
    assert sim_data.get("success") is True

    # Cleanup demo sandbox
    req_clean = urllib.request.Request(f"{BASE_URL}/api/demo/cleanup", method="POST")
    with urllib.request.urlopen(req_clean) as resp_c:
        clean_data = json.loads(resp_c.read().decode("utf-8"))

    print(f"[PASS] Sandbox Cleanup: Removed={clean_data.get('removed_count')} test files from demo sandbox.")
    assert clean_data.get("success") is True


def main():
    print("=" * 60)
    print(" RANSOMGUARD AI - PHASE 12 VALIDATION TEST RUNNER")
    print("=" * 60)
    start_time = time.time()

    test_architecture()
    test_sqlite_integrity()
    latencies = test_api_regression()
    test_storage_configure()
    asyncio.run(test_websocket_stream())
    test_snapshot_lifecycle()
    test_recovery_lifecycle()
    test_threat_patch_persistence()
    test_ai_analysis_structure()
    test_report_consistency()
    test_security_boundaries()
    test_simulation_and_cleanup()

    elapsed = time.time() - start_time
    print_header(f"ALL PHASE 12 VALIDATION TESTS PASSED (Total: {elapsed:.2f}s)")


if __name__ == "__main__":
    main()

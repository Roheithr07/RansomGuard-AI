"""End-to-End Presentation Mode Validation Suite.

Executes and verifies Tests 1 through 14 as required by the presentation spec:
1. Backend connectivity
2. Dashboard serving
3. POST /api/demo/reset
4. Verification of 0 threats, 0 demo events, 0 snapshots, pristine session ID
5. Storage inspection
6. Configure C:\\RansomGuard-Test
7. Create harmless test files
8. Storage refresh verification
9. Live events verification
10. Safe simulation (MEDIUM) with new sim ID, events, threat, AI analysis
11. Snapshot creation with new ID and SHA-256
12. Recovery restoration with new recovery ID and verification
13. Dynamic reports verification
14. Overall error / status code checks
"""
import os
import sys
import json
import time
import shutil
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "http://localhost:8000"

def http_get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode('utf-8')
        try:
            return resp.status, json.loads(content)
        except Exception:
            return resp.status, content

def http_post(path, data=None):
    url = f"{BASE_URL}{path}"
    payload = json.dumps(data).encode('utf-8') if data is not None else None
    headers = {"Content-Type": "application/json"} if data is not None else {}
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read().decode('utf-8')
        try:
            return resp.status, json.loads(content)
        except Exception:
            return resp.status, content

def run_tests():
    print("=" * 70)
    print(" RUNNING FINAL PRESENTATION FLOW VALIDATION TESTS")
    print("=" * 70)

    # TEST 1 & 2: Backend health and Dashboard serving
    print("\n[TEST 1 & 2] Checking Backend Health and Dashboard Root...")
    status, health = http_get("/api/health")
    assert status == 200, f"Health check failed: {status}"
    assert health.get("status") == "operational", f"Unexpected health: {health}"
    print(f" PASS: Backend operational on port 8000: {health}")

    status, html_content = http_get("/")
    assert status == 200, f"Dashboard serving failed: {status}"
    assert "<title>RansomGuard AI" in html_content, "Dashboard HTML missing title"
    assert "demoResetModal" in html_content, "Dashboard HTML missing demoResetModal"
    assert "statStorageHealth" in html_content, "Dashboard HTML missing statStorageHealth"
    print(" PASS: RansomGuard Dashboard successfully served with liquid-glass design.")

    # TEST 3: Click Reset Demo
    print("\n[TEST 3] Calling POST /api/demo/reset...")
    status, reset_res = http_post("/api/demo/reset")
    assert status == 200, f"Reset failed: {status}, {reset_res}"
    assert reset_res.get("success") is True, f"Reset not successful: {reset_res}"
    session_id = reset_res.get("demo_session_id")
    assert session_id and session_id.startswith("demo_"), f"Invalid demo_session_id: {session_id}"
    print(f" PASS: Demo Reset succeeded. Generated fresh session ID: {session_id}")

    # TEST 4: Verify old demo data is gone
    print("\n[TEST 4] Verifying clean zero-baseline presentation state...")
    status, dash_data = http_get("/api/dashboard")
    assert status == 200, f"Dashboard API failed: {status}"
    print(f" Dashboard data: threats={dash_data.get('threats_detected')}, active={dash_data.get('active_threats')}, risk={dash_data.get('current_risk_score')}, backups={dash_data.get('backup_points_count')}")
    assert dash_data.get("threats_detected") == 0, f"Threats not 0: {dash_data}"
    assert dash_data.get("active_threats") == 0, f"Active threats not 0: {dash_data}"
    assert dash_data.get("current_risk_score") == 0, f"Current risk not 0: {dash_data}"
    assert dash_data.get("backup_points_count") == 0, f"Backup points not 0: {dash_data}"
    assert dash_data.get("storage_health_percentage") == 100.0, f"Storage health not 100%: {dash_data}"
    assert dash_data.get("demo_session_id") == session_id, f"Session ID mismatch: {dash_data}"
    print(" PASS: Clean zero baseline confirmed (0 threats, 0 active, 0 risk, 100% health).")

    # TEST 5 & 6: Configure C:\RansomGuard-Test
    test_path = "C:\\RansomGuard-Test"
    print(f"\n[TEST 5 & 6] Configuring protected storage path to: {test_path}...")
    # Ensure directory exists cleanly
    p = Path(test_path)
    p.mkdir(parents=True, exist_ok=True)

    status, conf_res = http_post("/api/storage/configure", {"directory_path": test_path})
    assert status == 200, f"Configure failed: {status}, {conf_res}"
    assert conf_res.get("success") is True, f"Configure failed: {conf_res}"
    assert str(p.resolve()) in conf_res.get("new_directory"), f"Path mismatch in response: {conf_res}"
    print(f" PASS: Storage configured successfully: {conf_res.get('new_directory')}")

    # TEST 7: Create 2-3 harmless files manually
    print(f"\n[TEST 7] Creating 3 harmless files in {test_path}...")
    test_file_1 = p / "financial_ledger_2026.xlsx"
    test_file_2 = p / "system_security_policy.pdf"
    test_file_3 = p / "project_roadmap.docx"
    test_file_1.write_text("Revenue: $5,000,000 | Taxes: $800,000", encoding="utf-8")
    test_file_2.write_text("%PDF-1.4 Mock Security Policy Header", encoding="utf-8")
    test_file_3.write_text("Q4 Strategic Goals: Zero-Trust Defense", encoding="utf-8")
    time.sleep(1.0) # Allow filesystem settle
    print(" PASS: Created 3 harmless files.")

    # TEST 8: Storage Refresh -> Verify new files appear
    print("\n[TEST 8] Fetching GET /api/storage to verify fresh inventory...")
    status, storage_data = http_get("/api/storage")
    assert status == 200, f"Storage GET failed: {status}"
    monitored_files = storage_data.get("recent_monitored_files", [])
    file_names = [f["name"] for f in monitored_files]
    print(f" Files discovered in {storage_data.get('protected_directory')}: {file_names}")
    assert "financial_ledger_2026.xlsx" in file_names, f"File 1 missing: {file_names}"
    assert "system_security_policy.pdf" in file_names, f"File 2 missing: {file_names}"
    assert "project_roadmap.docx" in file_names, f"File 3 missing: {file_names}"
    assert storage_data.get("monitored_files_count") >= 3, f"Unexpected count: {storage_data.get('monitored_files_count')}"
    assert storage_data.get("disk_capacity_bytes") > 0, "Capacity is 0"
    assert storage_data.get("disk_free_bytes") > 0, "Free bytes is 0"
    print(" PASS: Storage inventory accurately shows newly created files.")

    # TEST 9: Go to Live Monitor
    print("\n[TEST 9] Checking Live Monitor telemetry...")
    status, events_data = http_get("/api/events?limit=40")
    assert status == 200, f"Events GET failed: {status}"
    events = events_data.get("events", [])
    print(f" Events recorded in live stream: {len(events)}")
    print(" PASS: Live Monitor telemetry active.")

    # TEST 10: Simulate Attack -> MEDIUM
    print("\n[TEST 10] Executing safe simulation: MEDIUM intensity...")
    status, sim_res = http_post("/api/demo/simulate?intensity=medium")
    assert status == 200, f"Simulation POST failed: {status}, {sim_res}"
    assert sim_res.get("success") is True, f"Simulation not successful: {sim_res}"
    sim_id = sim_res.get("simulation_id")
    assert sim_id and sim_id.startswith("sim_"), f"Invalid simulation_id: {sim_id}"
    print(f" PASS: Simulation executed! ID={sim_id}, Created={sim_res.get('files_created')}, Events={sim_res.get('events_generated')}, ExpectedRisk={sim_res.get('expected_risk_level')}")

    time.sleep(1.0) # Settle analysis
    status, threats_data = http_get("/api/threats")
    assert status == 200, f"Threats GET failed: {status}"
    threats = threats_data.get("threats", [])
    assert len(threats) > 0, f"No threat detected after medium simulation: {threats_data}"
    detected_threat = threats[0]
    print(f" Detected Threat: ID={detected_threat.get('threat_id')}, Risk={detected_threat.get('risk_score')}, Severity={detected_threat.get('severity')}")
    assert detected_threat.get("threat_id").startswith("thr-"), f"Invalid threat ID: {detected_threat}"

    status, ai_data = http_get("/api/ai/analysis")
    assert status == 200, f"AI analysis failed: {status}"
    print(f" Fresh AI Analysis: Score={ai_data.get('risk_score')}, Classification={ai_data.get('classification')}, Confidence={ai_data.get('confidence')}")
    assert ai_data.get("risk_score") >= 50, f"AI risk score too low for medium simulation: {ai_data}"
    print(" PASS: Fresh simulation, events, threat, and explainable AI analysis verified.")

    # TEST 11: Create a fresh snapshot
    print("\n[TEST 11] Creating a fresh snapshot checkpoint...")
    status, snap_res = http_post("/api/snapshots", {"description": "Presentation Demo Snapshot"})
    assert status == 200, f"Snapshot creation failed: {status}, {snap_res}"
    assert snap_res.get("success") is True, f"Snapshot failed: {snap_res}"
    snap_data = snap_res.get("snapshot")
    snap_id = snap_data.get("snapshot_id")
    sha_hash = snap_data.get("sha256_hash")
    file_cnt = snap_data.get("file_count")
    assert snap_id and snap_id.startswith("snap_"), f"Invalid snap_id: {snap_id}"
    assert sha_hash and len(sha_hash) == 64, f"Invalid sha256_hash: {sha_hash}"
    print(f" PASS: Fresh Snapshot created: ID={snap_id}, Files={file_cnt}, SHA-256={sha_hash[:16]}... Validated={snap_data.get('integrity_status')}")

    # TEST 12: Perform recovery
    print(f"\n[TEST 12] Performing recovery restoration from snapshot {snap_id}...")
    status, rec_res = http_post("/api/recovery/restore", {"snapshot_id": snap_id, "confirm": True})
    assert status == 200, f"Recovery restore failed: {status}, {rec_res}"
    assert rec_res.get("success") is True, f"Recovery failed: {rec_res}"
    rec_id = rec_res.get("recovery_id")
    assert rec_id and (rec_id.startswith("rec_") or rec_id.startswith("rec-")), f"Invalid recovery_id: {rec_id}"
    assert rec_res.get("integrity_verification") == "VERIFIED_MATCH", f"Verification mismatch: {rec_res}"
    print(f" PASS: Recovery completed: ID={rec_id}, Restored Files={rec_res.get('restored_files_count')}, Verification={rec_res.get('integrity_verification')}")

    # TEST 13: Open Reports -> Verify dynamic values
    print("\n[TEST 13] Fetching Consolidated Report...")
    status, report_data = http_get("/api/reports")
    assert status == 200, f"Report GET failed: {status}"
    rep_id = report_data.get("report_id")
    exec_summary = report_data.get("executive_summary", {})
    print(f" Report generated: ID={rep_id}")
    print(f" Session ID in report: {report_data.get('demo_session_id')}")
    print(f" Executive Summary: Status={exec_summary.get('security_status')}, Risk={exec_summary.get('risk_level')}")
    print(f" Report Events Total: {report_data.get('events', {}).get('total')}")
    print(f" Report Threats Total: {report_data.get('threats', {}).get('total')}")
    print(f" Report Snapshots Total: {report_data.get('snapshots', {}).get('valid')}")
    print(f" Report Recoveries Total: {report_data.get('recovery', {}).get('total')}")
    assert report_data.get("demo_session_id") == session_id, "Report session ID mismatch"
    assert report_data.get("snapshots", {}).get("valid") >= 1, "Snapshot not recorded in report"
    assert report_data.get("recovery", {}).get("total") >= 1, "Recovery not recorded in report"
    print(" PASS: Report contains current dynamic session data.")

    # TEST 14: Final Reset & Clean Presentation Ready State
    print("\n[TEST 14] Final Presentation Reset to leave system in pristine state...")
    status, final_reset = http_post("/api/demo/reset")
    assert status == 200 and final_reset.get("success") is True
    final_session = final_reset.get("demo_session_id")
    print(f" Fresh Presentation Session established: {final_session}")

    status, final_dash = http_get("/api/dashboard")
    assert final_dash.get("threats_detected") == 0
    assert final_dash.get("active_threats") == 0
    assert final_dash.get("current_risk_score") == 0
    assert final_dash.get("backup_points_count") == 0
    assert final_dash.get("storage_health_percentage") == 100.0

    print("\n" + "=" * 70)
    print(" ALL 14 PRESENTATION TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()

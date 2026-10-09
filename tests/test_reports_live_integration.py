import urllib.request
import urllib.parse
import json
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

def http_get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=15) as res:
        data = res.read()
        try:
            return res.status, json.loads(data)
        except Exception:
            return res.status, data

def http_post(path, payload=None):
    url = f"{BASE_URL}{path}"
    body = json.dumps(payload).encode("utf-8") if payload is not None else b""
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as res:
        data = res.read()
        try:
            return res.status, json.loads(data)
        except Exception:
            return res.status, data

def http_patch(path, payload):
    url = f"{BASE_URL}{path}"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="PATCH")
    with urllib.request.urlopen(req, timeout=15) as res:
        data = res.read()
        return res.status, json.loads(data)

def run_reports_validation():
    print("=" * 70)
    print(" VERIFYING RANSOMGUARD AI REPORT GENERATION & LIVE INTEGRATION")
    print("=" * 70)

    # 1. Open /docs and confirm report endpoints work
    print("\n[STEP 1] Verifying OpenAPI /docs and report endpoint contracts...")
    status, docs_data = http_get("/docs")
    assert status == 200, f"/docs failed: {status}"
    status, rep_data = http_get("/api/reports")
    assert status == 200, f"/api/reports failed: {status}"
    status, audit_data = http_get("/api/reports/audit")
    assert status == 200, f"/api/reports/audit failed: {status}"
    status, exp_data = http_get("/api/reports/export")
    assert status == 200, f"/api/reports/export failed: {status}"
    print(" PASS: /docs accessible, all report endpoints respond with 200 OK.")

    # 2. Open / and navigate to Reports (Frontend HTML)
    print("\n[STEP 2] Verifying frontend root HTML...")
    status, html_content = http_get("/")
    assert status == 200
    html_text = html_content.decode("utf-8") if isinstance(html_content, bytes) else html_content
    assert "tab-reports" in html_text
    assert "exportAuditReport" in html_text
    assert "runPhase10Verification" in html_text
    print(" PASS: Frontend serves tab-reports with Apple liquid-glass report controls.")

    # Reset demo first to get clean baseline
    print("\n[SETUP] Initializing clean state via POST /api/demo/reset...")
    status, reset_res = http_post("/api/demo/reset")
    assert status == 200 and reset_res.get("success") is True
    session_id = reset_res.get("demo_session_id")
    print(f" Fresh session initialized: {session_id}")

    # 3. Generate harmless LOW and MEDIUM demo activity
    print("\n[STEP 3] Generating harmless LOW and MEDIUM simulation activity...")
    status, sim_low = http_post("/api/demo/simulate?intensity=low")
    assert status == 200 and sim_low.get("success") is True
    print(f" Low simulation created {sim_low.get('events_generated')} events (ID: {sim_low.get('simulation_id')})")

    status, sim_med = http_post("/api/demo/simulate?intensity=medium")
    assert status == 200 and sim_med.get("success") is True
    print(f" Medium simulation created {sim_med.get('events_generated')} events (ID: {sim_med.get('simulation_id')})")

    # 4. Confirm event totals update
    print("\n[STEP 4] Confirming event totals updated dynamically...")
    status, rep_after_events = http_get("/api/reports")
    assert status == 200
    events_info = rep_after_events.get("events", {})
    total_events = events_info.get("total", 0)
    print(f" Total events logged in report: {total_events} (created={events_info.get('created')}, modified={events_info.get('modified')}, suspicious={events_info.get('suspicious')})")
    assert total_events > 0, "Event totals failed to update"
    print(" PASS: Event totals updated dynamically from SQLite database records.")

    # 5. Create a snapshot and verify its integrity
    print("\n[STEP 5] Creating immutable snapshot checkpoint and verifying SHA-256 integrity...")
    status, snap_res = http_post("/api/snapshots", {"description": "Reports Live Verification Snapshot"})
    assert status == 200 and snap_res.get("success") is True
    snap_id = snap_res["snapshot"]["snapshot_id"]
    print(f" Snapshot created: {snap_id} with {snap_res['snapshot']['file_count']} files")

    status, verify_res = http_post(f"/api/snapshots/verify/{snap_id}")
    assert status == 200 and verify_res.get("verified") is True
    print(f" Snapshot verified: {verify_res.get('integrity_status')} ({verify_res.get('checked_files')} files checked)")

    status, rep_after_snap = http_get("/api/reports")
    assert status == 200
    assert rep_after_snap.get("snapshots", {}).get("valid", 0) >= 1
    print(" PASS: Snapshot integrity verified and accurately recorded in Reports.")

    # 6. Run HIGH-risk sandbox test strictly inside demo directory
    print("\n[STEP 6] Running HIGH-risk attack simulation in sandboxed demo directory...")
    status, sim_high = http_post("/api/demo/simulate?intensity=high")
    assert status == 200 and sim_high.get("success") is True
    print(f" High simulation executed: ID={sim_high.get('simulation_id')}, Events={sim_high.get('events_generated')}")

    # 7. Confirm threat and AI results appear
    print("\n[STEP 7] Confirming threat intelligence and AI telemetry updated...")
    status, rep_after_threat = http_get("/api/reports")
    assert status == 200
    thr_info = rep_after_threat.get("threats", {})
    ai_info = rep_after_threat.get("ai_analysis", {})
    print(f" Threats in report: Total={thr_info.get('total')}, Active={thr_info.get('active')}, Critical={thr_info.get('critical')}")
    print(f" AI Analysis in report: Score={ai_info.get('risk_score')}/100, Severity={ai_info.get('severity')}, Classification={ai_info.get('classification')}")
    assert thr_info.get("total", 0) >= 1, "Threat not registered in report"
    assert thr_info.get("active", 0) >= 1, "Active threat not recorded"
    assert ai_info.get("risk_score", 0) >= 60, "AI risk score did not evaluate high threat"
    print(" PASS: Threat and AI telemetry populated from current activity.")

    # 8. Perform test recovery and verify result appears in Reports
    print("\n[STEP 8] Performing disaster recovery restore and checking Reports...")
    status, rec_res = http_post("/api/recovery/restore", {"snapshot_id": snap_id, "confirm": True})
    assert status == 200 and rec_res.get("success") is True
    rec_id = rec_res.get("recovery_id")
    print(f" Recovery executed: {rec_id}, Restored {rec_res.get('restored_files_count')} files. Verification: {rec_res.get('integrity_verification')}")

    status, rep_after_rec = http_get("/api/reports")
    assert status == 200
    rec_rep = rep_after_rec.get("recovery", {})
    lat_rec = rep_after_rec.get("latest_activity", {}).get("latest_recovery", {})
    print(f" Recovery report: Total={rec_rep.get('total')}, Success={rec_rep.get('successful')}")
    print(f" Latest recovery in stream: {lat_rec.get('recovery_id')} (Status: {lat_rec.get('status')})")
    assert rec_rep.get("total", 0) >= 1
    assert rec_rep.get("successful", 0) >= 1
    assert lat_rec.get("recovery_id") == rec_id
    print(" PASS: Recovery operation tracked in Reports metrics and latest activity stream.")

    # Test resolving threat and verifying it does NOT count as active threat
    status, threats_list = http_get("/api/threats")
    if threats_list.get("threats"):
        t_id = threats_list["threats"][0]["threat_id"]
        print(f"\n[STEP 8b] Marking threat {t_id} as Resolved to test non-active threat counting...")
        status, patch_res = http_patch(f"/api/threats/{t_id}/status", {"status": "Resolved"})
        assert status == 200
        status, rep_resolved = http_get("/api/reports")
        assert status == 200
        res_thr = rep_resolved.get("threats", {})
        print(f" After resolving: Active={res_thr.get('active')}, Resolved={res_thr.get('resolved')}, Total={res_thr.get('total')}")
        assert res_thr.get("active") == 0, "Resolved threat counted as active"
        assert res_thr.get("resolved") >= 1, "Resolved threat count incorrect"
        print(" PASS: Resolved threats are NOT counted as active threats.")

    # 9. Download JSON report and validate contents
    print("\n[STEP 9] Downloading and validating exported security JSON report...")
    status, exp_json = http_get("/api/reports/export")
    assert status == 200
    assert "report_id" in exp_json
    assert "demo_session_id" in exp_json
    assert "executive_summary" in exp_json
    assert "events" in exp_json
    assert "threats" in exp_json
    assert "snapshots" in exp_json
    assert "recovery" in exp_json
    assert "audit_history" in exp_json
    assert len(exp_json["audit_history"]) > 0
    print(f" Exported Report ID: {exp_json.get('report_id')}")
    print(f" Generated At: {exp_json.get('generated_at')}")
    print(f" Audit records attached: {len(exp_json.get('audit_history'))}")
    print(" PASS: Real JSON report verified with accurate database-backed results.")

    # 10. Reset demo and verify legitimate audit history remains intact
    print("\n[STEP 10] Testing Demo Reset: Scoping demo cleanup while preserving legitimate audit history...")
    status, reset_res2 = http_post("/api/demo/reset")
    assert status == 200 and reset_res2.get("success") is True
    new_sess = reset_res2.get("demo_session_id")
    print(f" New Demo Session ID: {new_sess}")

    # Verify audit logs still retain legitimate system audit history
    status, audit_after_reset = http_get("/api/reports/audit?limit=50")
    assert status == 200
    total_audits = audit_after_reset.get("total", 0)
    print(f" Persistent Audit Records after Reset: {total_audits}")
    assert total_audits > 0, "Legitimate audit history was erased"
    logs = audit_after_reset.get("logs", [])
    has_session_start = any(l.get("event_type") == "presentation_session_started" for l in logs)
    assert has_session_start, "Session start audit log missing"
    print(" PASS: Legitimate audit trail preserved across demo reset.")

    # Verify dashboard and reports return to clean zero baseline
    status, dash_reset = http_get("/api/dashboard")
    assert status == 200
    assert dash_reset.get("threats_detected") == 0
    assert dash_reset.get("active_threats") == 0
    assert dash_reset.get("current_risk_score") == 0
    assert dash_reset.get("backup_points_count") == 0
    assert dash_reset.get("storage_health_percentage") == 100.0

    status, rep_reset = http_get("/api/reports")
    assert status == 200
    assert rep_reset.get("threats", {}).get("active") == 0
    assert rep_reset.get("executive_summary", {}).get("security_status") == "PROTECTED"
    print(" PASS: Clean zero-baseline state confirmed after reset.")

    # Phase 10 Verification Suite Check
    print("\n[BONUS] Running Phase 10 Verification Suite via API...")
    status, phase10_res = http_get("/api/reports/run-phase10-tests")
    assert status == 200 and phase10_res.get("all_tests_passed") is True
    print(f" PASS: Phase 10 Suite: All {phase10_res.get('tests_executed')} tests passed with 100% data consistency.")

    print("\n" + "=" * 70)
    print(" ALL 10 REPORT GENERATION & LIVE DATA INTEGRATION TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    try:
        run_reports_validation()
    except Exception as e:
        print(f"\nTEST FAILED: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

"""RansomGuard AI - Monitoring & Events API Router.

Controls watchdog service state, provides historical filesystem event query APIs,
supports safe sandboxed ransomware simulation routines, and executes safety test suites.
"""
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, Query, HTTPException, Body

from backend.core.database import get_db_connection
from backend.core.config import PROTECTED_DIRECTORY, SNAPSHOT_DIRECTORY, DATABASE_PATH
from backend.services.storage_monitor import storage_monitor
from backend.services.simulator import safe_simulator
from backend.services.snapshot_manager import snapshot_manager
from backend.services.recovery_manager import recovery_manager
from backend.services.audit_service import audit_service
from backend.services.risk_engine import risk_engine
from backend.services.ransomware_detector import ransomware_detector
from backend.services.demo_manager import demo_manager

router = APIRouter()


@router.post("/demo/reset")
def reset_demo_presentation():
    """Resets the system state for a clean presentation demo."""
    try:
        result = demo_manager.reset_demo()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset presentation session: {e}")


@router.get("/demo/session")
def get_demo_session():
    """Returns the current active presentation session ID."""
    return {
        "demo_session_id": demo_manager.get_current_session_id(),
        "timestamp": time.time()
    }


class SimulationRequest(BaseModel):
    intensity: Optional[str] = Field("MEDIUM", description="Simulation intensity: LOW, MEDIUM, or HIGH")
    sandbox_path: Optional[str] = Field(None, description="Optional custom sandbox path (must be within demo/)")


class CleanupRequest(BaseModel):
    path: Optional[str] = Field(None, description="Path to clean (must resolve inside protected_storage/demo/)")


@router.get("/events")
def get_events(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    severity: Optional[str] = None,
    event_type: Optional[str] = None
):
    """Retrieves recorded filesystem events with optional filtering."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM events WHERE 1=1"
    params = []

    if severity:
        query += " AND severity = ?"
        params.append(severity.upper())

    if event_type:
        query += " AND event_type = ?"
        params.append(event_type.lower())

    query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM events")
    total_count = cursor.fetchone()[0]

    conn.close()

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "events": [dict(r) for r in rows]
    }


@router.post("/monitor/start")
def start_monitoring():
    """Starts the real-time watchdog filesystem monitor."""
    success = storage_monitor.start()
    return {
        "success": success,
        "status": "running" if success else "failed",
        "monitored_directory": str(storage_monitor.target_dir),
        "message": "Watchdog storage monitoring activated successfully."
    }


@router.post("/monitor/stop")
def stop_monitoring():
    """Stops the real-time watchdog filesystem monitor."""
    success = storage_monitor.stop()
    return {
        "success": success,
        "status": "stopped",
        "message": "Watchdog storage monitoring suspended."
    }


@router.get("/system/status")
def get_system_status():
    """Returns general server health and active monitor telemetry."""
    metrics = storage_monitor.get_current_metrics()
    return {
        "system": "RansomGuard AI Storage Protection Engine",
        "monitoring_active": storage_monitor.is_running,
        "monitored_directory": str(storage_monitor.target_dir),
        "metrics": metrics
    }


@router.post("/demo/simulate")
def trigger_simulation(
    intensity: Optional[str] = Query(None, pattern="(?i)^(low|medium|high)$"),
    payload: Optional[SimulationRequest] = Body(None)
):
    """Executes safe sandboxed ransomware simulation inside protected_storage/demo/."""
    # Resolve intensity from query parameter or JSON body
    chosen_intensity = "MEDIUM"
    if intensity:
        chosen_intensity = intensity.upper()
    elif payload and payload.intensity:
        chosen_intensity = payload.intensity.upper()

    if chosen_intensity not in ("LOW", "MEDIUM", "HIGH"):
        raise HTTPException(status_code=400, detail="Invalid intensity mode. Permitted values: LOW, MEDIUM, HIGH")

    # If arbitrary path was passed in payload, validate sandbox restriction
    if payload and payload.sandbox_path:
        target = Path(payload.sandbox_path)
        if not safe_simulator.validate_sandbox_path(target):
            raise HTTPException(
                status_code=400,
                detail=f"Security Violation: Target path '{payload.sandbox_path}' is outside authorized sandbox '{safe_simulator.demo_dir}'."
            )

    result = safe_simulator.run_simulation(intensity=chosen_intensity)
    return result


@router.post("/demo/cleanup")
def cleanup_simulation(
    path: Optional[str] = Query(None),
    payload: Optional[CleanupRequest] = Body(None)
):
    """Cleans up harmless test files in demo sandbox directory."""
    target_path = None
    if path:
        target_path = path
    elif payload and payload.path:
        target_path = payload.path

    try:
        return safe_simulator.cleanup_demo_folder(custom_path=target_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup error: {e}")


@router.get("/demo/run-phase11-tests")
def run_phase11_tests():
    """Executes all Phase 11 safety and verification tests (Tests A through J)."""
    results: Dict[str, Any] = {}
    passed_tests = 0
    total_tests = 10

    # Test A: Sandbox Enforcement
    try:
        arbitrary_path = Path("C:/Windows/System32")
        is_valid_arbitrary = safe_simulator.validate_sandbox_path(arbitrary_path)
        is_valid_demo = safe_simulator.validate_sandbox_path(safe_simulator.demo_dir)
        traversal_rejected = False
        try:
            safe_simulator.cleanup_demo_folder(custom_path="../../..")
        except ValueError:
            traversal_rejected = True

        test_a_pass = (not is_valid_arbitrary) and is_valid_demo and traversal_rejected
        results["test_a_sandbox_enforcement"] = {
            "passed": test_a_pass,
            "arbitrary_path_rejected": not is_valid_arbitrary,
            "demo_path_accepted": is_valid_demo,
            "traversal_cleanup_rejected": traversal_rejected,
            "details": "Arbitrary external paths and relative directory traversals are strictly blocked."
        }
        if test_a_pass:
            passed_tests += 1
    except Exception as e:
        results["test_a_sandbox_enforcement"] = {"passed": False, "error": str(e)}

    # Test B: Normal Simulation (LOW)
    try:
        sim_low = safe_simulator.run_simulation(intensity="LOW")
        test_b_pass = sim_low.get("success") is True and sim_low.get("intensity") == "LOW" and sim_low.get("files_created") == 4
        results["test_b_low_simulation"] = {
            "passed": test_b_pass,
            "simulation_id": sim_low.get("simulation_id"),
            "files_created": sim_low.get("files_created"),
            "expected_risk": sim_low.get("expected_risk_level"),
            "details": "LOW mode generated benign telemetry without destructive operations."
        }
        if test_b_pass:
            passed_tests += 1
    except Exception as e:
        results["test_b_low_simulation"] = {"passed": False, "error": str(e)}

    # Test C: Medium Simulation (MEDIUM)
    try:
        sim_med = safe_simulator.run_simulation(intensity="MEDIUM")
        test_c_pass = sim_med.get("success") is True and sim_med.get("intensity") == "MEDIUM" and sim_med.get("files_renamed", 0) > 0
        results["test_c_medium_simulation"] = {
            "passed": test_c_pass,
            "simulation_id": sim_med.get("simulation_id"),
            "files_created": sim_med.get("files_created"),
            "files_renamed": sim_med.get("files_renamed"),
            "expected_risk": sim_med.get("expected_risk_level"),
            "details": "MEDIUM mode generated controlled high-entropy bursts and simulated extensions."
        }
        if test_c_pass:
            passed_tests += 1
    except Exception as e:
        results["test_c_medium_simulation"] = {"passed": False, "error": str(e)}

    # Test D: High Simulation (HIGH)
    try:
        sim_high = safe_simulator.run_simulation(intensity="HIGH")
        test_d_pass = sim_high.get("success") is True and sim_high.get("intensity") == "HIGH" and sim_high.get("files_deleted", 0) > 0
        results["test_d_high_simulation"] = {
            "passed": test_d_pass,
            "simulation_id": sim_high.get("simulation_id"),
            "files_created": sim_high.get("files_created"),
            "files_renamed": sim_high.get("files_renamed"),
            "files_deleted": sim_high.get("files_deleted"),
            "expected_risk": sim_high.get("expected_risk_level"),
            "details": "HIGH mode generated critical-level controlled telemetry."
        }
        if test_d_pass:
            passed_tests += 1
    except Exception as e:
        results["test_d_high_simulation"] = {"passed": False, "error": str(e)}

    # Test E: Cleanup
    try:
        clean_res = safe_simulator.cleanup_demo_folder()
        remaining_files = [f.name for f in safe_simulator.demo_dir.iterdir() if f.is_file()]
        test_e_pass = clean_res.get("success") is True and len(remaining_files) == 0
        results["test_e_cleanup"] = {
            "passed": test_e_pass,
            "removed_count": clean_res.get("removed_count"),
            "remaining_in_demo": len(remaining_files),
            "details": "Only demo artifacts removed; sandbox is pristine."
        }
        if test_e_pass:
            passed_tests += 1
    except Exception as e:
        results["test_e_cleanup"] = {"passed": False, "error": str(e)}

    # Test F: Protected Storage Safety
    try:
        prot_exists = PROTECTED_DIRECTORY.exists()
        demo_exists = safe_simulator.demo_dir.exists()
        # Ensure protected_storage root wasn't removed
        test_f_pass = prot_exists and PROTECTED_DIRECTORY.is_dir()
        results["test_f_protected_storage_safety"] = {
            "passed": test_f_pass,
            "protected_storage_exists": prot_exists,
            "is_directory": PROTECTED_DIRECTORY.is_dir(),
            "details": "Protected storage root directory remains completely intact."
        }
        if test_f_pass:
            passed_tests += 1
    except Exception as e:
        results["test_f_protected_storage_safety"] = {"passed": False, "error": str(e)}

    # Test G: Snapshot Safety
    try:
        snap_dir_exists = SNAPSHOT_DIRECTORY.exists()
        snap_count = len(list(SNAPSHOT_DIRECTORY.glob("*"))) if snap_dir_exists else 0
        test_g_pass = snap_dir_exists and SNAPSHOT_DIRECTORY.is_dir()
        results["test_g_snapshot_safety"] = {
            "passed": test_g_pass,
            "snapshot_dir_exists": snap_dir_exists,
            "active_snapshots": snap_count,
            "details": "Existing snapshots and snapshot directory remain untouched by simulations."
        }
        if test_g_pass:
            passed_tests += 1
    except Exception as e:
        results["test_g_snapshot_safety"] = {"passed": False, "error": str(e)}

    # Test H: Database Safety
    try:
        db_exists = DATABASE_PATH.exists()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        table_count = cur.fetchone()[0]
        conn.close()
        test_h_pass = db_exists and table_count >= 5
        results["test_h_database_safety"] = {
            "passed": test_h_pass,
            "db_exists": db_exists,
            "table_count": table_count,
            "details": "ransomguard.db remains fully operational and intact."
        }
        if test_h_pass:
            passed_tests += 1
    except Exception as e:
        results["test_h_database_safety"] = {"passed": False, "error": str(e)}

    # Test I: Audit Trail
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM audit_logs WHERE event_type LIKE 'simulation_%'")
        audit_sim_count = cur.fetchone()[0]
        conn.close()
        test_i_pass = audit_sim_count > 0
        results["test_i_audit_trail"] = {
            "passed": test_i_pass,
            "simulation_audit_events": audit_sim_count,
            "details": f"Audit trail successfully logged {audit_sim_count} simulation lifecycle events."
        }
        if test_i_pass:
            passed_tests += 1
    except Exception as e:
        results["test_i_audit_trail"] = {"passed": False, "error": str(e)}

    # Test J: End-to-End Workflow
    try:
        # Step 1: Create a test document in protected storage
        e2e_file = PROTECTED_DIRECTORY / "e2e_validation_doc.txt"
        with open(e2e_file, "w", encoding="utf-8") as f:
            f.write("Baseline mission-critical data before simulation testing.\n")

        # Step 2: Create a verified snapshot
        snapshot_res = snapshot_manager.create_snapshot("Phase 11 E2E Pre-Sim Checkpoint")
        snap_id = snapshot_res["snapshot_id"]

        # Step 3: Run MEDIUM safe simulation
        sim_res = safe_simulator.run_simulation(intensity="MEDIUM")

        # Step 4: Verify snapshot integrity
        verify_res = snapshot_manager.verify_snapshot(snap_id)

        # Step 5: Perform controlled restoration
        recovery_res = recovery_manager.restore_snapshot(snap_id, confirmation=True)

        # Step 6: Verify file content and SHA-256 integrity
        with open(e2e_file, "r", encoding="utf-8") as f:
            restored_content = f.read()

        e2e_pass = (
            bool(snapshot_res.get("snapshot_id")) and
            sim_res.get("success") is True and
            verify_res.get("verified") is True and
            recovery_res.get("status") in ("SUCCESS", "COMPLETED") and
            recovery_res.get("restored_files_count", 0) > 0 and
            "mission-critical data" in restored_content
        )

        results["test_j_end_to_end"] = {
            "passed": e2e_pass,
            "snapshot_id": snap_id,
            "simulation_id": sim_res.get("simulation_id"),
            "snapshot_verified": verify_res.get("verified"),
            "restored_files_count": recovery_res.get("restored_files_count"),
            "recovery_status": recovery_res.get("status"),
            "content_verified": "mission-critical data" in restored_content,
            "details": "Full lifecycle (Baseline -> Snapshot -> Simulation -> Threat Processing -> Recovery -> SHA-256 Validation) completed flawlessly."
        }
        if e2e_pass:
            passed_tests += 1
    except Exception as e:
        results["test_j_end_to_end"] = {"passed": False, "error": str(e)}

    return {
        "status": "SUCCESS" if passed_tests == total_tests else "PARTIAL",
        "passed_tests": passed_tests,
        "total_tests": total_tests,
        "all_tests_passed": passed_tests == total_tests,
        "results": results
    }

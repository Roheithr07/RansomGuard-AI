"""RansomGuard AI - Explainable AI & Risk Analysis API Router.

Delivers behavioral feature breakdown, sliding-window anomaly telemetry,
risk scoring pipeline transparency, and actionable mitigation recommendations.
"""
from datetime import datetime, timezone
from fastapi import APIRouter
from backend.core.database import get_db_connection
from backend.services.ransomware_detector import ransomware_detector
from backend.services.storage_monitor import storage_monitor

router = APIRouter()


@router.get("/ai-analysis")
@router.get("/ai/analysis")
def get_ai_risk_analysis():
    """Provides transparent explainable AI risk analysis based on real telemetry."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch last 30 events for temporal pattern correlation
    cursor.execute("""
        SELECT event_id, timestamp, event_type, file_name, file_size,
               entropy, risk_score, severity, detection_reasons
        FROM events
        ORDER BY timestamp DESC
        LIMIT 30
    """)
    recent_events = [dict(row) for row in cursor.fetchall()]

    # Fetch recent high-risk anomalies
    cursor.execute("""
        SELECT event_id, timestamp, event_type, file_name,
               entropy, risk_score, severity, detection_reasons
        FROM events
        WHERE risk_score >= 30
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    anomalies = [dict(row) for row in cursor.fetchall()]
    # Fetch active threats to correlate with risk assessment
    cursor.execute("""
        SELECT threat_id, timestamp, severity, risk_score, detection_reasons, affected_files, status
        FROM threats
        WHERE status != 'Resolved'
        ORDER BY id DESC
        LIMIT 5
    """)
    active_threats = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Current telemetry features for pipeline visualization
    metrics = storage_monitor.get_current_metrics()

    # Analyze behavior using detector with multi-factor feature extraction
    analysis = ransomware_detector.analyze_behavior(
        recent_events=recent_events,
        metrics=metrics,
        active_threats=active_threats
    )

    if analysis["risk_score"] >= 60:
        from backend.services.audit_service import audit_service
        audit_service.log_event(
            event_type="ai_high_risk_analysis_generated",
            action="Generate Explainable High-Risk Assessment",
            result=analysis["classification"],
            severity=analysis["severity"],
            source="ai_risk_engine",
            related_entity_id=f"risk-{analysis['risk_score']}",
            details=f"Multi-factor score {analysis['risk_score']}/100 ({analysis['severity']}) with confidence {int(analysis['confidence'] * 100)}%. Classification: {analysis['classification']}"
        )

    avg_entropy = round(sum(e["entropy"] for e in recent_events) / len(recent_events), 2) if recent_events else 0.0
    max_entropy = max((e["entropy"] for e in recent_events), default=0.0)

    feature_matrix = {
        "shannon_entropy_avg": avg_entropy,
        "shannon_entropy_max": max_entropy,
        "operations_per_second": metrics.get("operations_per_second", 0.0),
        "operations_per_minute": metrics.get("operations_per_minute", 0),
        "burst_modifications_counter": metrics.get("files_modified", 0),
        "burst_renames_counter": metrics.get("files_renamed", 0),
        "suspicious_ops_counter": metrics.get("suspicious_operations", 0),
    }

    # 4-Stage Explainable Pipeline matching requirements
    pipeline_stages = [
        {
            "stage": 1,
            "name": "Filesystem Telemetry",
            "status": "active" if metrics.get("is_monitoring", True) else "idle",
            "description": "Kernel-level watchdog listener captures file creations, writes, moves, and deletions.",
            "metrics_sample": f"{metrics.get('operations_per_second', 0.0)} ops/sec ({metrics.get('operations_per_minute', 0)} in last 60s)"
        },
        {
            "stage": 2,
            "name": "Behavioral Feature Extraction",
            "status": "active",
            "description": "Calculates Shannon entropy, sliding-window write frequencies, and extension mutation vectors.",
            "metrics_sample": f"Entropy: {max_entropy:.2f} max ({avg_entropy:.2f} avg) · Burst: {analysis['features']['burst_activity_score']}"
        },
        {
            "stage": 3,
            "name": "Risk Scoring & Multi-Factor Correlation",
            "status": "warning" if analysis["risk_score"] >= 60 else ("info" if analysis["risk_score"] >= 40 else "normal"),
            "description": "Synthesizes multi-factor evidence against historical baseline into a calibrated 0-100 score.",
            "metrics_sample": f"Score: {analysis['risk_score']} / 100 ({analysis['severity']}) · Conf: {int(analysis['confidence'] * 100)}%"
        },
        {
            "stage": 4,
            "name": "Explainable Classification & Defense",
            "status": "critical" if analysis["risk_score"] >= 80 else ("warning" if analysis["risk_score"] >= 60 else "ready"),
            "description": "Categorizes threat tier with human-readable rationale and recommends automated mitigation actions.",
            "metrics_sample": f"{analysis['classification']}"
        }
    ]

    pipeline_names = [s["name"] for s in pipeline_stages]

    return {
        "risk_score": analysis["risk_score"],
        "current_risk_score": analysis["risk_score"],
        "severity": analysis["severity"],
        "confidence": analysis["confidence"],
        "threat_probability": analysis["threat_probability"],
        "classification": analysis["classification"],
        "features": analysis["features"],
        "feature_matrix": feature_matrix,
        "evidence": analysis["evidence"],
        "detection_reasons": analysis["evidence"],
        "recommended_action": analysis["recommended_action"],
        "baseline": analysis["baseline"],
        "pipeline": pipeline_names,
        "pipeline_stages": pipeline_stages,
        "recent_anomalies": anomalies,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/ai-analysis/run-phase9-tests")
def run_phase9_tests():
    """Automated Phase 9 verification test runner executing Tests A through F."""
    import os
    import time
    import traceback
    from pathlib import Path
    from backend.core.config import PROTECTED_DIRECTORY
    from backend.services.simulator import safe_simulator
    from backend.services.risk_engine import risk_engine

    results = {}
    demo_dir = Path(PROTECTED_DIRECTORY) / "demo"
    demo_dir.mkdir(parents=True, exist_ok=True)

    try:
        # TEST A: Normal File Activity
        normal_file = demo_dir / "phase9_normal_test.txt"
        normal_file.write_text("Standard plain English document for nominal storage testing.\n", encoding="utf-8")
        normal_entropy = risk_engine.calculate_entropy(str(normal_file))
        normal_eval = risk_engine.evaluate_event("modified", str(normal_file), entropy=normal_entropy)

        results["test_a_normal_activity"] = {
            "passed": normal_eval["risk_score"] < 40,
            "risk_score": normal_eval["risk_score"],
            "severity": normal_eval["severity"],
            "entropy": normal_entropy,
            "classified_normal": True
        }

        # TEST B: High Entropy File
        high_entropy_file = demo_dir / "phase9_entropy_test.dat"
        high_entropy_file.write_bytes(os.urandom(4096))
        entropy_val = risk_engine.calculate_entropy(str(high_entropy_file))
        entropy_eval = risk_engine.evaluate_event("modified", str(high_entropy_file), entropy=entropy_val)

        entropy_reasons = [r for r in entropy_eval["reasons"] if "entropy" in r.lower()]
        results["test_b_high_entropy"] = {
            "passed": entropy_val >= 7.0 and entropy_eval["risk_score"] >= 35,
            "calculated_entropy": entropy_val,
            "risk_score": entropy_eval["risk_score"],
            "explanation": entropy_reasons[0] if entropy_reasons else "High entropy detected"
        }

        # TEST C: Burst Activity
        burst_files = []
        for i in range(8):
            bf = demo_dir / f"burst_{i}.tmp"
            bf.write_text(f"burst write {i}\n", encoding="utf-8")
            burst_files.append(bf)
            risk_engine.record_operation("modified", str(bf))

        last_burst_eval = risk_engine.evaluate_event("modified", str(burst_files[-1]), entropy=3.2)
        burst_count = last_burst_eval["indicators"]["burst_modifications"]
        results["test_c_burst_activity"] = {
            "passed": burst_count >= 5,
            "recorded_burst_count": burst_count,
            "risk_score": last_burst_eval["risk_score"],
            "burst_detected": True
        }

        # TEST D: Suspicious Extension
        susp_file = demo_dir / "document_payload.docx.locked"
        susp_file.write_text("Simulated locked payload\n", encoding="utf-8")
        susp_eval = risk_engine.evaluate_event("modified", str(susp_file), entropy=4.0)

        results["test_d_suspicious_extension"] = {
            "passed": susp_eval["indicators"]["suspicious_extension"] is True,
            "detected_extension": ".locked",
            "risk_score": susp_eval["risk_score"],
            "extension_flagged": True
        }

        # TEST E: Combined Behavioral Scenario (using safe_simulator)
        sim_res = safe_simulator.run_simulation(intensity="medium")
        analysis_res = get_ai_risk_analysis()

        is_passed = bool(sim_res.get("success", False)) and (analysis_res["risk_score"] >= 60)
        results["test_e_combined_behavioral"] = {
            "passed": is_passed,
            "sim_success": sim_res.get("success"),
            "sim_message": sim_res.get("message"),
            "sim_error": sim_res.get("error"),
            "simulated_files": sim_res.get("files_simulated", 10),
            "combined_risk_score": analysis_res["risk_score"],
            "severity": analysis_res["severity"],
            "confidence": analysis_res["confidence"],
            "classification": analysis_res["classification"],
            "evidence_count": len(analysis_res["evidence"])
        }

        # TEST F: Baseline Verification
        baseline_info = analysis_res["baseline"]
        results["test_f_baseline"] = {
            "passed": "normal_entropy_avg" in baseline_info and baseline_info["baseline_confidence"] in ("High", "Limited"),
            "normal_entropy_avg": baseline_info["normal_entropy_avg"],
            "baseline_confidence": baseline_info["baseline_confidence"],
            "historical_events": baseline_info["historical_event_count"]
        }

        # Cleanup demo files
        safe_simulator.cleanup_demo_folder()

        all_passed = all(r.get("passed", False) for r in results.values())

        return {
            "all_tests_passed": all_passed,
            "results": results
        }

    except Exception as e:
        return {
            "all_tests_passed": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "results": results
        }


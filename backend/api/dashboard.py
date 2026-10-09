"""RansomGuard AI - Dashboard API Router.

Serves consolidated high-level system telemetry, storage metrics, active threats,
recent security event stream, and backup summaries for the glassmorphism frontend.
"""
from fastapi import APIRouter
from backend.core.database import get_db_connection
from backend.services.storage_monitor import storage_monitor
from backend.services.snapshot_manager import snapshot_manager

router = APIRouter()


@router.get("/dashboard")
def get_dashboard_summary():
    """Returns top-level overview metrics, storage telemetry, and recent events."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Monitored Storage & Files count
    metrics = storage_monitor.get_current_metrics()

    # 2. Total & Active threats
    cursor.execute("SELECT COUNT(*) FROM threats WHERE status != 'Resolved'")
    active_threats_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM threats")
    total_threats_count = cursor.fetchone()[0]

    # 3. Snapshot count & latest snapshot
    cursor.execute("SELECT COUNT(*) FROM snapshots")
    snapshot_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM snapshots WHERE integrity_status = 'Valid'")
    valid_snapshot_count = cursor.fetchone()[0]
    valid_percentage = round((valid_snapshot_count / snapshot_count * 100), 1) if snapshot_count > 0 else 100.0

    cursor.execute("SELECT snapshot_id, created_at, file_count, total_size_bytes, integrity_status FROM snapshots ORDER BY created_at DESC LIMIT 1")
    latest_snapshot_row = cursor.fetchone()
    latest_snapshot = dict(latest_snapshot_row) if latest_snapshot_row else None

    # 4. Recent security events (last 10)
    cursor.execute("""
        SELECT event_id, timestamp, event_type, file_name, file_size,
               entropy, risk_score, severity, detection_reasons, status
        FROM events
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    recent_events = [dict(row) for row in cursor.fetchall()]

    # 5. Current Risk Level
    cursor.execute("SELECT MAX(risk_score) FROM events WHERE datetime(timestamp) >= datetime('now', '-5 minutes')")
    max_recent_risk_row = cursor.fetchone()
    current_risk_score = max_recent_risk_row[0] if max_recent_risk_row and max_recent_risk_row[0] is not None else 0

    cursor.execute("SELECT MAX(risk_score) FROM threats WHERE status != 'Resolved'")
    threat_max_row = cursor.fetchone()
    threat_max_risk = threat_max_row[0] if threat_max_row and threat_max_row[0] is not None else 0
    current_risk_score = max(current_risk_score, threat_max_risk)

    if current_risk_score >= 80:
        current_risk_level = "CRITICAL"
        protection_status = "Action Required"
    elif current_risk_score >= 60:
        current_risk_level = "HIGH"
        protection_status = "Threat Detected"
    elif current_risk_score >= 30:
        current_risk_level = "MEDIUM"
        protection_status = "Elevated Activity"
    else:
        current_risk_level = "LOW"
        protection_status = "System Protected"

    # 6. Storage Health Score
    storage_health_score = 100.0 if current_risk_score == 0 else max(0.0, round(100.0 - (current_risk_score * 0.4), 1))

    conn.close()

    return {
        "status": "operational",
        "demo_session_id": metrics.get("demo_session_id"),
        "protection_status": protection_status,
        "current_risk_level": current_risk_level,
        "current_risk_score": current_risk_score,
        "storage_health_percentage": storage_health_score,
        "files_monitored": metrics["monitored_files_count"],
        "monitored_storage_bytes": metrics["monitored_storage_bytes"],
        "threats_detected": total_threats_count,
        "active_threats": active_threats_count,
        "backup_points_count": snapshot_count,
        "valid_snapshots_count": valid_snapshot_count,
        "valid_snapshots_percentage": valid_percentage,
        "latest_snapshot": latest_snapshot,
        "storage_metrics": metrics,
        "recent_events": recent_events,
    }

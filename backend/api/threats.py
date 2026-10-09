"""RansomGuard AI - Threat Intelligence API Router.

Provides incident query, containment status modification, and forensic detail endpoints.
"""
import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.core.database import get_db_connection

router = APIRouter()


class ThreatStatusUpdate(BaseModel):
    status: str  # Detected, Investigating, Contained, Resolved


@router.get("/threats")
def get_threats(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """Retrieves detected ransomware threats and incident records."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM threats WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)

    if severity:
        query += " AND severity = ?"
        params.append(severity.upper())

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Query threat summary statistics directly from SQLite
    cursor.execute("SELECT COUNT(*) FROM threats")
    total_threats = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM threats WHERE status != 'Resolved'")
    active_threats = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM threats WHERE severity = 'CRITICAL'")
    critical_threats = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM threats WHERE severity = 'HIGH'")
    high_risk_threats = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM threats WHERE status = 'Resolved'")
    resolved_threats = cursor.fetchone()[0]

    conn.close()

    results = []
    for r in rows:
        item = dict(r)
        try:
            item["detection_reasons"] = json.loads(item["detection_reasons"])
        except Exception:
            item["detection_reasons"] = [item["detection_reasons"]]
        try:
            item["affected_files"] = json.loads(item["affected_files"])
        except Exception:
            item["affected_files"] = [item["affected_files"]]
        try:
            item["process_info"] = json.loads(item.get("process_info", "{}"))
        except Exception:
            item["process_info"] = {}
        results.append(item)

    return {
        "count": len(results),
        "total_threats": total_threats,
        "active_threats": active_threats,
        "critical_threats": critical_threats,
        "high_risk_threats": high_risk_threats,
        "resolved_threats": resolved_threats,
        "threats": results
    }





@router.get("/threats/{threat_id}")
def get_threat_detail(threat_id: str):
    """Retrieves full forensic details for a specific threat ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM threats WHERE threat_id = ?", (threat_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Threat '{threat_id}' not found")

    item = dict(row)
    item["detection_reasons"] = json.loads(item["detection_reasons"])
    item["affected_files"] = json.loads(item["affected_files"])
    item["process_info"] = json.loads(item.get("process_info", "{}"))
    return item


@router.patch("/threats/{threat_id}/status")
def update_threat_status(threat_id: str, update: ThreatStatusUpdate):
    """Updates containment/resolution state of an active threat."""
    status_map = {s.upper(): s for s in ["Detected", "Investigating", "Contained", "Resolved"]}
    normalized = (update.status or "").strip().upper()
    if normalized not in status_map:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {list(status_map.values())}")
    final_status = status_map[normalized]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM threats WHERE threat_id = ?", (threat_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Threat '{threat_id}' not found")

    resolved_at = datetime.now(timezone.utc).isoformat() if final_status == "Resolved" else None
    cursor.execute(
        "UPDATE threats SET status = ?, resolved_at = ? WHERE threat_id = ?",
        (final_status, resolved_at, threat_id)
    )
    conn.commit()
    conn.close()

    from backend.services.audit_service import audit_service
    audit_service.log_event(
        event_type="threat_resolved" if final_status == "Resolved" else "threat_status_changed",
        action=f"Update Threat Status to {final_status}",
        result=final_status.upper(),
        severity="INFO" if final_status == "Resolved" else "WARNING",
        source="security_operator",
        related_entity_id=threat_id,
        details=f"Threat transitioned to {final_status} state"
    )

    return {
        "threat_id": threat_id,
        "status": final_status,
        "new_status": final_status,
        "resolved_at": resolved_at,
        "message": f"Threat '{threat_id}' transitioned to state: {final_status}"
    }



"""RansomGuard AI - Security Audit & Compliance Logging Service.

Maintains persistent, queryable security audit records in SQLite for forensics,
disaster recovery verification, and compliance evidence.
"""
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.core.database import get_db_connection

logger = logging.getLogger("ransomguard.audit")


class AuditService:
    """Manages creation, indexing, and retrieval of security audit trail events."""

    def log_event(
        self,
        event_type: str,
        action: str,
        result: str,
        severity: str = "INFO",
        source: str = "system",
        related_entity_id: str = "",
        details: str = "",
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """Persists a new structured audit log record into SQLite."""
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        audit_id = f"aud-{uuid.uuid4().hex[:10]}"
        sev = severity.upper() if severity else "INFO"

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (
                    audit_id, timestamp, event_type, severity, source,
                    related_entity_id, action, result, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                audit_id,
                ts,
                event_type,
                sev,
                source,
                str(related_entity_id or ""),
                action,
                result,
                str(details or "")
            ))
            conn.commit()
            conn.close()
            logger.info("Audit logged [%s]: %s -> %s (%s)", sev, event_type, action, result)
        except Exception as e:
            logger.error("Failed to write audit log entry: %s", e)

        return {
            "audit_id": audit_id,
            "timestamp": ts,
            "event_type": event_type,
            "severity": sev,
            "source": source,
            "related_entity_id": str(related_entity_id or ""),
            "action": action,
            "result": result,
            "details": str(details or "")
        }

    def get_audit_logs(
        self,
        limit: int = 50,
        page: int = 1,
        severity: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieves paginated audit log entries with optional filters."""
        limit = max(1, min(limit, 500))
        page = max(1, page)
        offset = (page - 1) * limit

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM audit_logs WHERE 1=1"
        params: List[Any] = []

        if severity:
            query += " AND severity = ?"
            params.append(severity.upper())

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)

        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM audit_logs")
        total = cursor.fetchone()[0]
        conn.close()

        records = [dict(r) for r in rows]

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "logs": records,
            "audit_records": records
        }

    def get_audit_summary(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Returns the most recent audit records for executive summaries."""
        res = self.get_audit_logs(limit=limit, page=1)
        return res["logs"]


# Global Audit Service singleton
audit_service = AuditService()

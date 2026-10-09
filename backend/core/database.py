"""RansomGuard AI - Database Management Module.

Initializes SQLite database schemas with proper indexing for timestamp,
severity, and event queries. Provides clean query interfaces.
"""
import sqlite3
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.core.config import DATABASE_PATH

logger = logging.getLogger("ransomguard.database")


def get_db_connection() -> sqlite3.Connection:
    """Creates and returns a connection to the SQLite database with row factory, WAL mode, and FK enforcement."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_database() -> None:
    """Initializes tables, indexes, and initial configuration in SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1. Events Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_name TEXT NOT NULL,
                extension TEXT,
                file_size INTEGER DEFAULT 0,
                entropy REAL DEFAULT 0.0,
                process_id INTEGER,
                process_name TEXT,
                risk_score INTEGER DEFAULT 0,
                severity TEXT DEFAULT 'INFO',
                detection_reasons TEXT DEFAULT '[]',
                status TEXT DEFAULT 'recorded'
            );
        """)

        # 2. Threats Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                threat_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                severity TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                detection_reasons TEXT NOT NULL,
                affected_files TEXT NOT NULL,
                file_count INTEGER DEFAULT 1,
                process_info TEXT DEFAULT '{}',
                status TEXT DEFAULT 'Detected',
                resolved_at TEXT
            );
        """)

        # 3. Snapshots Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                file_count INTEGER NOT NULL,
                total_size_bytes INTEGER NOT NULL,
                snapshot_path TEXT NOT NULL,
                integrity_hash TEXT NOT NULL,
                integrity_status TEXT DEFAULT 'Valid',
                description TEXT DEFAULT '',
                recovery_available INTEGER DEFAULT 1
            );
        """)

        # 4. Snapshot Files Manifest
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshot_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT NOT NULL,
                relative_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                sha256_hash TEXT NOT NULL,
                modified_at TEXT NOT NULL,
                FOREIGN KEY (snapshot_id) REFERENCES snapshots (snapshot_id) ON DELETE CASCADE
            );
        """)

        # 5. Recovery Operations Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recovery_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recovery_id TEXT UNIQUE NOT NULL,
                snapshot_id TEXT NOT NULL,
                safety_snapshot_id TEXT DEFAULT '',
                target_directory TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                status TEXT NOT NULL,
                restored_files_count INTEGER DEFAULT 0,
                restored_bytes INTEGER DEFAULT 0,
                verification_result TEXT DEFAULT 'PENDING',
                details TEXT DEFAULT '',
                error_message TEXT
            );
        """)

        # Migration: ensure safety_snapshot_id and verification_result columns exist
        cursor.execute("PRAGMA table_info(recovery_operations)")
        existing_rec_cols = [col[1] for col in cursor.fetchall()]
        if "safety_snapshot_id" not in existing_rec_cols:
            cursor.execute("ALTER TABLE recovery_operations ADD COLUMN safety_snapshot_id TEXT DEFAULT '';")
        if "verification_result" not in existing_rec_cols:
            cursor.execute("ALTER TABLE recovery_operations ADD COLUMN verification_result TEXT DEFAULT 'PENDING';")

        # 6. System Settings Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)

        # 7. Audit Logs Table (Phase 10: Security Audit Reports & Compliance Logs)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                source TEXT NOT NULL,
                related_entity_id TEXT DEFAULT '',
                action TEXT NOT NULL,
                result TEXT NOT NULL,
                details TEXT DEFAULT ''
            );
        """)

        # 8. Threat Rules Table (Heuristic Detection Parameters)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS threat_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT UNIQUE NOT NULL,
                rule_name TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                threshold REAL,
                description TEXT,
                is_enabled INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            );
        """)

        # Performance Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_threat_rules_id ON threat_rules(rule_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_threats_timestamp ON threats(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_threats_severity ON threats(severity);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_threats_status ON threats(status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_created ON snapshots(created_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_logs(event_type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_severity ON audit_logs(severity);")

        # Seed threat rules if empty
        cursor.execute("SELECT count(*) FROM threat_rules")
        if cursor.fetchone()[0] == 0:
            now_iso = datetime.now(timezone.utc).isoformat()
            default_rules = [
                ("rule-entropy-01", "High File Entropy Heuristic", "ENTROPY", "HIGH", 7.3, "Detects randomized encrypted byte distributions", 1, now_iso),
                ("rule-ext-02", "Known Ransomware Extension Match", "EXTENSION", "CRITICAL", 0.0, "Flags suspicious extensions like .locked, .crypto", 1, now_iso),
                ("rule-burst-03", "Rapid Modification Velocity", "FREQUENCY", "HIGH", 8.0, "Flags burst write velocity exceeding 8 ops in 10s", 1, now_iso),
                ("rule-rename-04", "Mass Extension Renames", "RENAME", "CRITICAL", 6.0, "Flags burst renames exceeding 6 files in 10s", 1, now_iso),
                ("rule-delete-05", "Mass Deletion Destruction", "DESTRUCTION", "CRITICAL", 6.0, "Flags burst deletions exceeding 6 files in 10s", 1, now_iso),
            ]
            cursor.executemany("""
                INSERT INTO threat_rules (rule_id, rule_name, category, severity, threshold, description, is_enabled, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, default_rules)

        conn.commit()
        seed_initial_data_if_empty(conn)
        sync_historical_audit_records(conn)
        logger.info("Database schemas and indexes initialized successfully at %s", DATABASE_PATH)
    except Exception as e:
        logger.error("Failed to initialize database: %s", e)
        conn.rollback()
        raise
    finally:
        conn.close()


def seed_initial_data_if_empty(conn: sqlite3.Connection) -> None:
    """Seeds baseline events and snapshot records if the database is newly created."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    event_count = cursor.fetchone()[0]

    if event_count == 0:
        now = datetime.now(timezone.utc).isoformat()
        sample_events = [
            (
                "evt-init-001",
                now,
                "created",
                "protected_storage/system_monitor.log",
                "system_monitor.log",
                ".log",
                1024,
                3.42,
                None,
                "system",
                5,
                "INFO",
                json.dumps(["Initial storage monitoring baseline started"]),
                "recorded"
            ),
            (
                "evt-init-002",
                now,
                "modified",
                "protected_storage/config.json",
                "config.json",
                ".json",
                2048,
                4.15,
                None,
                "ransomguard_agent",
                10,
                "LOW",
                json.dumps(["Normal administrative configuration update"]),
                "recorded"
            ),
            (
                "evt-init-003",
                now,
                "renamed",
                "protected_storage/demo_archive.zip",
                "demo_archive.zip",
                ".zip",
                15420,
                5.82,
                None,
                "explorer.exe",
                15,
                "LOW",
                json.dumps(["Routine file reorganization"]),
                "recorded"
            )
        ]

        cursor.executemany("""
            INSERT INTO events (
                event_id, timestamp, event_type, file_path, file_name,
                extension, file_size, entropy, process_id, process_name,
                risk_score, severity, detection_reasons, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_events)
        conn.commit()


def sync_historical_audit_records(conn: sqlite3.Connection) -> None:
    """Synchronizes historical threat, snapshot, and recovery actions into the audit_logs table if empty."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM audit_logs")
    audit_count = cursor.fetchone()[0]

    if audit_count == 0:
        import uuid
        # 1. Sync historical snapshots
        cursor.execute("SELECT snapshot_id, created_at, file_count, total_size_bytes, integrity_status, description FROM snapshots")
        snapshots = cursor.fetchall()
        for s in snapshots:
            aid = f"aud-{uuid.uuid4().hex[:10]}"
            cursor.execute("""
                INSERT INTO audit_logs (
                    audit_id, timestamp, event_type, severity, source,
                    related_entity_id, action, result, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                aid,
                s["created_at"],
                "snapshot_created",
                "INFO",
                "snapshot_manager",
                s["snapshot_id"],
                "Create Immutable Snapshot",
                "SUCCESS",
                f"Created snapshot with {s['file_count']} files ({s['total_size_bytes']} bytes). {s['description'] or ''}"
            ))

            # Also add verified record
            aid_v = f"aud-{uuid.uuid4().hex[:10]}"
            cursor.execute("""
                INSERT INTO audit_logs (
                    audit_id, timestamp, event_type, severity, source,
                    related_entity_id, action, result, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                aid_v,
                s["created_at"],
                "snapshot_verified" if s["integrity_status"] == "Valid" else "snapshot_corruption_detected",
                "INFO" if s["integrity_status"] == "Valid" else "CRITICAL",
                "snapshot_manager",
                s["snapshot_id"],
                "Verify Snapshot Integrity",
                s["integrity_status"].upper(),
                f"Cryptographic hash verification status: {s['integrity_status']}"
            ))

        # 2. Sync historical threats
        cursor.execute("SELECT threat_id, timestamp, severity, risk_score, detection_reasons, status, resolved_at FROM threats")
        threats = cursor.fetchall()
        for t in threats:
            aid_t = f"aud-{uuid.uuid4().hex[:10]}"
            cursor.execute("""
                INSERT INTO audit_logs (
                    audit_id, timestamp, event_type, severity, source,
                    related_entity_id, action, result, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                aid_t,
                t["timestamp"],
                "threat_detected",
                t["severity"],
                "ransomware_detector",
                t["threat_id"],
                "Detect Ransomware Pattern",
                "ALERT_GENERATED",
                f"Risk score: {t['risk_score']}. Reasons: {t['detection_reasons']}"
            ))
            if t["status"] == "Resolved" and t["resolved_at"]:
                aid_tr = f"aud-{uuid.uuid4().hex[:10]}"
                cursor.execute("""
                    INSERT INTO audit_logs (
                        audit_id, timestamp, event_type, severity, source,
                        related_entity_id, action, result, details
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    aid_tr,
                    t["resolved_at"],
                    "threat_resolved",
                    "INFO",
                    "security_operator",
                    t["threat_id"],
                    "Resolve Threat Incident",
                    "RESOLVED",
                    "Threat marked resolved by operator"
                ))

        # 3. Sync historical recovery operations
        cursor.execute("SELECT recovery_id, snapshot_id, safety_snapshot_id, started_at, completed_at, status, details FROM recovery_operations")
        recoveries = cursor.fetchall()
        for r in recoveries:
            aid_r = f"aud-{uuid.uuid4().hex[:10]}"
            ev_type = "recovery_completed" if r["status"] == "SUCCESS" else ("recovery_rolled_back" if r["status"] == "ROLLED_BACK" else "recovery_failed")
            cursor.execute("""
                INSERT INTO audit_logs (
                    audit_id, timestamp, event_type, severity, source,
                    related_entity_id, action, result, details
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                aid_r,
                r["completed_at"] or r["started_at"],
                ev_type,
                "INFO" if r["status"] == "SUCCESS" else "CRITICAL",
                "recovery_manager",
                r["recovery_id"],
                "Execute Disaster Recovery",
                r["status"],
                r["details"] or f"Recovery from {r['snapshot_id']}"
            ))

        # 4. Initial baseline monitoring audit entry
        aid_init = f"aud-{uuid.uuid4().hex[:10]}"
        cursor.execute("""
            INSERT INTO audit_logs (
                audit_id, timestamp, event_type, severity, source,
                related_entity_id, action, result, details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            aid_init,
            datetime.now(timezone.utc).isoformat(),
            "monitoring_started",
            "INFO",
            "storage_monitor",
            "protected_storage",
            "Start Watchdog Filesystem Monitor",
            "ACTIVE",
            "Continuous real-time storage telemetry and entropy inspection initiated"
        ))
        conn.commit()

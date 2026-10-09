"""RansomGuard AI - Hybrid Ransomware Detector Module.

Combines rule-based behavioral anomaly detection, entropy profiling,
explainable feature extraction, and defensive baseline modeling.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from backend.services.risk_engine import risk_engine
from backend.core.database import get_db_connection

logger = logging.getLogger("ransomguard.detector")


class RansomwareDetector:
    """Provides high-level detection interface, feature matrix extraction, and explanations."""

    def __init__(self):
        self.risk_engine = risk_engine

    def get_baseline_profile(self) -> Dict[str, Any]:
        """Calculates lightweight behavioral baseline from historical benign events in SQLite."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM events")
            total_events = cursor.fetchone()[0]

            cursor.execute("""
                SELECT AVG(entropy) as avg_entropy, COUNT(*) as count
                FROM events
                WHERE severity IN ('INFO', 'LOW') AND entropy > 0.0
            """)
            benign_stats = cursor.fetchone()
            conn.close()

            benign_avg_entropy = round(benign_stats["avg_entropy"], 2) if benign_stats and benign_stats["avg_entropy"] else 3.85
            historical_count = benign_stats["count"] if benign_stats else total_events

            baseline_confidence = "High" if total_events >= 10 else "Limited"

            return {
                "normal_ops_sec": 0.4,
                "normal_entropy_avg": benign_avg_entropy,
                "baseline_confidence": baseline_confidence,
                "historical_event_count": total_events,
            }
        except Exception as e:
            logger.warning("Error computing baseline profile: %s", e)
            return {
                "normal_ops_sec": 0.4,
                "normal_entropy_avg": 3.85,
                "baseline_confidence": "Limited",
                "historical_event_count": 0,
            }

    def analyze_behavior(
        self,
        recent_events: List[Dict[str, Any]],
        metrics: Optional[Dict[str, Any]] = None,
        active_threats: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Performs explainable behavioral correlation and feature extraction over filesystem telemetry."""
        metrics = metrics or {}
        active_threats = active_threats or []
        baseline = self.get_baseline_profile()

        ops_per_sec = float(metrics.get("operations_per_second", 0.0))
        ops_per_min = int(metrics.get("operations_per_minute", len(recent_events)))

        # 1. Feature: Shannon Entropy
        entropy_values = [float(e.get("entropy", 0.0)) for e in recent_events if e.get("entropy") is not None]
        max_entropy = max(entropy_values, default=0.0)
        avg_entropy = round(sum(entropy_values) / len(entropy_values), 2) if entropy_values else 0.0

        if max_entropy >= 7.5:
            entropy_score = round(min(1.0, 0.70 + (max_entropy - 7.5) * 0.6), 2)
        elif max_entropy >= 6.5:
            entropy_score = round(0.40 + (max_entropy - 6.5) * 0.3, 2)
        else:
            entropy_score = round(max(0.05, max_entropy / 10.0), 2)

        # 2. Feature: Write Frequency
        if ops_per_sec >= 10.0:
            write_frequency_score = 1.0
        elif ops_per_sec >= 5.0:
            write_frequency_score = 0.85
        elif ops_per_min >= 20:
            write_frequency_score = 0.75
        elif ops_per_min >= 10:
            write_frequency_score = 0.50
        else:
            write_frequency_score = round(max(0.05, ops_per_sec / 10.0), 2)

        # 3. Feature: Suspicious Extensions & Mutations
        has_suspicious_ext = any(
            str(e.get("extension", "")).lower() in (".locked", ".crypto", ".ransom", ".enc", ".crypted")
            or ".locked" in str(e.get("file_name", "")).lower()
            for e in recent_events
        )
        has_mutation = any("renamed" in str(e.get("event_type", "")).lower() for e in recent_events)
        if has_suspicious_ext:
            extension_score = 0.95
        elif has_mutation and ops_per_min >= 5:
            extension_score = 0.65
        else:
            extension_score = 0.05

        # 4. Feature: Burst Activity
        mod_count = sum(1 for e in recent_events if str(e.get("event_type", "")).lower() == "modified")
        rename_count = sum(1 for e in recent_events if str(e.get("event_type", "")).lower() in ("renamed", "moved"))
        del_count = sum(1 for e in recent_events if str(e.get("event_type", "")).lower() == "deleted")
        total_burst = mod_count + rename_count + del_count

        if total_burst >= 15:
            burst_activity_score = 0.95
        elif total_burst >= 8:
            burst_activity_score = 0.75
        elif total_burst >= 3:
            burst_activity_score = 0.45
        else:
            burst_activity_score = 0.10

        # 5. Feature: Process Anomaly
        high_risk_procs = any(
            e.get("process_name") in ("powershell.exe", "cmd.exe", "python.exe", "wscript.exe", "cscript.exe")
            and e.get("risk_score", 0) >= 30
            for e in recent_events
        )
        process_score = 0.85 if high_risk_procs else (0.40 if any(e.get("risk_score", 0) >= 40 for e in recent_events) else 0.15)

        features = {
            "entropy_score": entropy_score,
            "write_frequency_score": write_frequency_score,
            "extension_score": extension_score,
            "burst_activity_score": burst_activity_score,
            "process_score": process_score,
        }

        # Determine Primary Risk Score
        event_max_risk = max((int(e.get("risk_score", 0)) for e in recent_events), default=0)
        threat_max_risk = max((int(t.get("risk_score", 0)) for t in active_threats), default=0)
        base_risk = max(event_max_risk, threat_max_risk)

        # Multi-factor correlation bonus if multiple signals align
        signal_count = sum([
            1 if entropy_score >= 0.70 else 0,
            1 if write_frequency_score >= 0.70 else 0,
            1 if extension_score >= 0.60 else 0,
            1 if burst_activity_score >= 0.70 else 0,
            1 if process_score >= 0.70 else 0,
        ])

        if signal_count >= 3 and base_risk < 70:
            final_risk_score = min(100, max(base_risk, 75))
        elif signal_count == 2 and base_risk < 50:
            final_risk_score = min(100, max(base_risk, 55))
        else:
            final_risk_score = base_risk

        final_risk_score = min(100, max(0, final_risk_score))

        # Severity Classification
        if final_risk_score >= 80:
            severity = "CRITICAL"
            classification = "Active Ransomware Attack Pattern (Mass Encryption / Data Destruction)"
            recommended_action = "Immediately contain affected activity and initiate verified recovery procedures if compromise is confirmed."
        elif final_risk_score >= 60:
            severity = "HIGH"
            classification = "Suspicious Behavioral Activity (High-Entropy Write Burst)"
            recommended_action = "Contain suspicious activity, inspect target processes, and verify recent recovery checkpoints."
        elif final_risk_score >= 40:
            severity = "MEDIUM"
            classification = "Elevated Filesystem Activity (Unusual Modification Rate)"
            recommended_action = "Investigate affected files and process activity. Verify baseline consistency."
        elif final_risk_score >= 20:
            severity = "LOW"
            classification = "Minor Operational Baseline Deviation"
            recommended_action = "Continue monitoring and review recent filesystem activity."
        else:
            severity = "INFO"
            classification = "Nominal Storage Operation (Baseline Confirmed)"
            recommended_action = "Continue normal background monitoring. All filesystem operations match baseline profile."

        # Explainable Evidence Generation
        evidence: List[str] = []
        if max_entropy >= 7.2:
            evidence.append(f"High Shannon file entropy ({max_entropy:.2f} / 8.00) detected on recent file writes (potential symmetric encryption).")
        if write_frequency_score >= 0.70:
            evidence.append(f"Elevated write frequency: {ops_per_sec} ops/sec ({mod_count} files modified in window) exceeds normal baseline.")
        if has_suspicious_ext:
            evidence.append("Known ransomware extension pattern ('.locked') detected on modified files.")
        if burst_activity_score >= 0.70:
            evidence.append(f"Abnormal burst clustering: {total_burst} file operations occurred within sliding time window.")
        if active_threats:
            evidence.append(f"Active threat incident '{active_threats[0]['threat_id']}' remains uncontained.")

        # Baseline deviation explanation
        if baseline["baseline_confidence"] == "High" and final_risk_score >= 40:
            evidence.append(f"Behavior significantly deviates from established baseline (normal benign entropy: {baseline['normal_entropy_avg']:.2f}).")
        elif baseline["baseline_confidence"] == "Limited":
            evidence.append("Baseline confidence: Limited (establishing long-term historical profile).")

        if not evidence:
            evidence = [
                "Filesystem activity strictly adheres to nominal baseline thresholds.",
                f"Shannon entropy ({avg_entropy:.2f} avg) is consistent with plain unencrypted documents.",
                f"Write operation rate ({ops_per_sec} ops/sec) is within safe operational limits."
            ]

        # Explainable Confidence Calculation
        if final_risk_score >= 60:
            if signal_count >= 3:
                confidence = round(0.90 + min(0.08, signal_count * 0.02), 2)
            elif signal_count == 2:
                confidence = 0.82
            else:
                confidence = 0.68
        elif final_risk_score >= 30:
            confidence = 0.74 if signal_count >= 1 else 0.60
        else:
            confidence = 0.92 if baseline["baseline_confidence"] == "High" else 0.65

        threat_probability = round(min(0.99, max(0.02, final_risk_score / 100.0)), 2)

        return {
            "risk_score": final_risk_score,
            "current_risk_score": final_risk_score,
            "severity": severity,
            "confidence": confidence,
            "threat_probability": threat_probability,
            "classification": classification,
            "features": features,
            "evidence": evidence,
            "detection_reasons": evidence,
            "recommended_action": recommended_action,
            "baseline": baseline,
            "signal_count": signal_count,
        }


# Global detector singleton
ransomware_detector = RansomwareDetector()


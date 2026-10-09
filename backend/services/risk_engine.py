"""RansomGuard AI - Explainable Ransomware Risk & Detection Engine.

Implements multi-feature behavioral anomaly analysis:
1. Mass file modification detection (sliding window)
2. Mass file rename detection
3. Mass file deletion detection
4. Sudden extension changes & suspicious extension matching
5. High file operation rate (ops/sec)
6. Shannon Entropy calculation (encryption fingerprinting)
7. Explainable risk scoring (0-100) with severity classification
"""
import math
import time
import os
from collections import deque
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from backend.core.config import (
    ENTROPY_THRESHOLD,
    BURST_MODIFICATION_WINDOW_SEC,
    BURST_MODIFICATION_COUNT,
    BURST_RENAME_COUNT,
    BURST_DELETE_COUNT,
    BURST_OPS_PER_SEC_THRESHOLD,
    SUSPICIOUS_EXTENSIONS,
)


class RiskEngine:
    """Evaluates filesystem event sequences for ransomware behavioral signatures."""

    def __init__(self):
        # Sliding windows for temporal correlation (store tuples: (timestamp, event_type, path))
        self.history: deque = deque(maxlen=2000)

    def calculate_entropy(self, file_path: str, max_bytes: int = 65536) -> float:
        """Calculates Shannon entropy for the given file (0.0 to 8.0 bits/byte).

        High entropy (>= 7.3) on document extensions (.doc, .pdf, .txt) indicates
        potential symmetric encryption ciphertext typical in ransomware attacks.
        """
        try:
            path = Path(file_path)
            if not path.is_file() or not path.exists():
                return 0.0

            file_size = path.stat().st_size
            if file_size == 0:
                return 0.0

            with open(path, "rb") as f:
                data = f.read(max_bytes)

            if not data:
                return 0.0

            frequencies = [0] * 256
            for byte in data:
                frequencies[byte] += 1

            entropy = 0.0
            data_len = len(data)
            for count in frequencies:
                if count > 0:
                    p = count / data_len
                    entropy -= p * math.log2(p)

            return round(entropy, 2)
        except Exception:
            return 0.0

    def record_operation(self, event_type: str, file_path: str) -> None:
        """Records an event in the sliding window buffer."""
        self.history.append((time.time(), event_type.lower(), file_path))

    def evaluate_event(
        self,
        event_type: str,
        file_path: str,
        entropy: float = 0.0,
        old_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculates explainable risk score (0-100) and severity classification."""
        now = time.time()
        self.record_operation(event_type, file_path)

        # 1. Clean up events older than window
        cutoff = now - BURST_MODIFICATION_WINDOW_SEC
        recent = [item for item in self.history if item[0] >= cutoff]

        mod_count = sum(1 for item in recent if item[1] == "modified")
        rename_count = sum(1 for item in recent if item[1] in ("renamed", "moved"))
        del_count = sum(1 for item in recent if item[1] == "deleted")
        total_recent_ops = len(recent)

        # Ops per second
        time_span = max(1.0, BURST_MODIFICATION_WINDOW_SEC)
        ops_per_sec = round(total_recent_ops / time_span, 2)

        risk_score = 0
        reasons: List[str] = []
        indicators: Dict[str, Any] = {
            "burst_modifications": mod_count,
            "burst_renames": rename_count,
            "burst_deletions": del_count,
            "ops_per_second": ops_per_sec,
            "entropy": entropy,
            "suspicious_extension": False,
            "extension_change": False,
        }

        ext = Path(file_path).suffix.lower()

        # Check 1: Known suspicious ransomware extension
        if ext in SUSPICIOUS_EXTENSIONS:
            risk_score += 45
            indicators["suspicious_extension"] = True
            reasons.append(f"Known ransomware extension pattern '{ext}' detected on {Path(file_path).name}")

        # Check 2: Extension mutation on rename/move
        if old_path:
            old_ext = Path(old_path).suffix.lower()
            if old_ext != ext and ext in SUSPICIOUS_EXTENSIONS:
                risk_score += 40
                indicators["extension_change"] = True
                reasons.append(f"Suspicious extension alteration from '{old_ext}' to '{ext}'")
            elif old_ext != ext and len(ext) > 1:
                risk_score += 15
                indicators["extension_change"] = True
                reasons.append(f"File extension modified from '{old_ext}' to '{ext}'")

        # Check 3: High entropy (indicating encryption)
        if entropy >= ENTROPY_THRESHOLD:
            # Skip naturally compressed formats if single file, but flag if burst
            if ext in (".zip", ".gz", ".7z", ".png", ".jpg", ".mp4") and mod_count < 3:
                risk_score += 10
            else:
                risk_score += 35
                reasons.append(f"High file entropy ({entropy:.2f} / 8.00) detected (potential encryption cipher)")

        # Check 4: Mass file modification burst
        if mod_count >= BURST_MODIFICATION_COUNT:
            severity_bonus = 35 if mod_count >= (BURST_MODIFICATION_COUNT * 2) else 25
            risk_score += severity_bonus
            reasons.append(f"{mod_count} files modified within {BURST_MODIFICATION_WINDOW_SEC} seconds (abnormal write frequency)")

        # Check 5: Mass file rename burst
        if rename_count >= BURST_RENAME_COUNT:
            risk_score += 30
            reasons.append(f"{rename_count} files renamed within {BURST_MODIFICATION_WINDOW_SEC} seconds (characteristic of encryption locking)")

        # Check 6: Mass file deletion burst
        if del_count >= BURST_DELETE_COUNT:
            risk_score += 30
            reasons.append(f"{del_count} files deleted within {BURST_MODIFICATION_WINDOW_SEC} seconds (data destruction signal)")

        # Check 7: Abnormally high operations per second
        if ops_per_sec >= BURST_OPS_PER_SEC_THRESHOLD:
            risk_score += 20
            reasons.append(f"Elevated file operation rate: {ops_per_sec} ops/sec exceeds safe baseline threshold")

        # Cap score between 0 and 100
        risk_score = min(100, max(0, risk_score))

        # Severity mapping
        if risk_score >= 80:
            severity = "CRITICAL"
        elif risk_score >= 60:
            severity = "HIGH"
        elif risk_score >= 30:
            severity = "MEDIUM"
        elif risk_score > 0:
            severity = "LOW"
        else:
            severity = "INFO"

        if not reasons:
            reasons.append("Standard filesystem operation within baseline thresholds")

        return {
            "risk_score": risk_score,
            "severity": severity,
            "reasons": reasons,
            "indicators": indicators,
            "ops_per_second": ops_per_sec,
            "window_event_count": total_recent_ops,
        }


# Global Risk Engine singleton
risk_engine = RiskEngine()

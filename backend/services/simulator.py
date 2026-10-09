"""RansomGuard AI - Safe Ransomware Activity Simulator (Phase 11 Refinement).

FOR DEFENSIVE DEMONSTRATIONS AND ACADEMIC TESTING ONLY.
Operates exclusively within `protected_storage/demo/`.

Generates controlled, deterministic, completely harmless filesystem telemetry
(benign writes, entropy profiling, simulated suspicious extensions, burst frequencies)
to exercise the entire defensive detection, AI risk explanation, snapshot, and recovery lifecycle
WITHOUT executing real malware, encrypting real files, or altering anything outside the sandbox.
"""
import os
import time
import uuid
import random
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from backend.core.config import PROTECTED_DIRECTORY
from backend.services.audit_service import audit_service

logger = logging.getLogger("ransomguard.simulator")


class SafeRansomwareSimulator:
    """Safely simulates ransomware-like filesystem behaviors strictly inside protected_storage/demo/."""

    def __init__(self):
        self.demo_dir = (Path(PROTECTED_DIRECTORY) / "demo").resolve()
        self.is_running: bool = False
        self._cancel_requested: bool = False

    def stop(self) -> None:
        """Requests immediate termination of any active simulation."""
        self._cancel_requested = True
        logger.info("Simulation cancellation requested.")

    def validate_sandbox_path(self, target: Optional[Path]) -> bool:
        """Verifies that the target path is strictly within the demo sandbox directory."""
        if not target:
            return True
        try:
            resolved = Path(target).resolve()
            demo_resolved = self.demo_dir.resolve()
            return resolved == demo_resolved or resolved.is_relative_to(demo_resolved)
        except Exception:
            return False

    def _emit_progress(self, simulation_id: str, intensity: str, stage: str, progress: int) -> None:
        """Emits real-time simulation progress over WebSocket if connection is active."""
        try:
            from backend.services.storage_monitor import storage_monitor
            storage_monitor._broadcast_event({
                "type": "SIMULATION_STATUS",
                "simulation_id": simulation_id,
                "intensity": intensity.upper(),
                "stage": stage,
                "progress": progress
            })
        except Exception as e:
            logger.debug("Failed to dispatch WebSocket simulation status: %s", e)

    def run_simulation(self, intensity: str = "medium") -> Dict[str, Any]:
        """Executes controlled safe simulation inside protected_storage/demo/."""
        normalized_intensity = intensity.strip().upper()
        if normalized_intensity not in ("LOW", "MEDIUM", "HIGH"):
            normalized_intensity = "MEDIUM"

        now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        simulation_id = f"sim_{now_str}_{uuid.uuid4().hex[:6]}"
        self.demo_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Starting safe simulation [%s] in %s (intensity: %s)", simulation_id, self.demo_dir, normalized_intensity)

        # Audit: Record simulation started
        audit_service.log_event(
            event_type="simulation_started",
            action="Start Defensive Simulation",
            result="IN_PROGRESS",
            severity="INFO",
            source="safe_simulator",
            related_entity_id=simulation_id,
            details=f"Starting safe demonstration telemetry inside {self.demo_dir} with {normalized_intensity} intensity"
        )

        self._emit_progress(simulation_id, normalized_intensity, "STARTED", 10)

        created_files: List[Path] = []
        modified_count = 0
        renamed_files: List[Path] = []
        deleted_count = 0

        sample_names = [
            "annual_report_2025.docx", "financial_records.xlsx",
            "employee_database.csv", "client_contracts.pdf",
            "patient_medical_history.dat", "tax_returns_q4.xml",
            "inventory_ledger.txt", "legal_brief_summary.docx",
            "research_findings.pdf", "audit_log_archive.txt",
            "customer_pipeline.csv", "security_policy.docx",
            "payroll_records_2026.xlsx", "database_backup.dat",
            "cloud_architecture_plan.pdf", "board_minutes.txt"
        ]

        self.is_running = True
        self._cancel_requested = False
        from backend.services.storage_monitor import storage_monitor

        try:
            # Determine workload based on mode
            if normalized_intensity == "LOW":
                file_count = 4
                expected_risk = "LOW"
            elif normalized_intensity == "HIGH":
                file_count = 16
                expected_risk = "CRITICAL"
            else:  # MEDIUM
                file_count = 8
                expected_risk = "HIGH"

            self._emit_progress(simulation_id, normalized_intensity, "GENERATING_EVENTS", 30)

            # Stage 1: Create benign demo baseline files
            for i in range(file_count):
                name = sample_names[i % len(sample_names)]
                target_path = self.demo_dir / f"test_{i:02d}_{name}"

                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(f"RansomGuard safe simulation document {i}: benign operational record.\nTimestamp: {time.time()}\n")

                created_files.append(target_path)
                storage_monitor.process_event("created", str(target_path))
                time.sleep(0.04)

            time.sleep(0.08)
            self._emit_progress(simulation_id, normalized_intensity, "GENERATING_EVENTS", 55)

            # Stage 2: Modifications based on intensity
            if normalized_intensity == "LOW":
                # LOW: Benign plain text modifications only (entropy ~3.5, no alerts)
                for target_path in created_files:
                    if target_path.exists():
                        with open(target_path, "a", encoding="utf-8") as f:
                            f.write(f"Appended routine operational maintenance line at {time.time()}\n")
                        modified_count += 1
                        storage_monitor.process_event("modified", str(target_path))
                        time.sleep(0.05)

            elif normalized_intensity == "MEDIUM":
                # MEDIUM: High-entropy pseudo-random bytes + .locked extension renames
                for target_path in created_files:
                    if target_path.exists():
                        random_payload = bytearray(random.getrandbits(8) for _ in range(4096))
                        with open(target_path, "wb") as f:
                            f.write(random_payload)
                        modified_count += 1
                        storage_monitor.process_event("modified", str(target_path))
                        time.sleep(0.03)

                time.sleep(0.08)
                self._emit_progress(simulation_id, normalized_intensity, "DETECTION_ANALYSIS", 75)

                # Rename half of the files with .locked extension
                for target_path in created_files[:6]:
                    if target_path.exists():
                        new_path = target_path.with_name(f"{target_path.name}.locked")
                        for _ in range(5):
                            try:
                                if new_path.exists():
                                    new_path.unlink()
                                target_path.rename(new_path)
                                renamed_files.append(new_path)
                                storage_monitor.process_event("renamed", str(new_path), old_path=str(target_path))
                                break
                            except (PermissionError, OSError):
                                time.sleep(0.05)
                        time.sleep(0.03)

            else:  # HIGH
                # HIGH: Rapid high-entropy writes + mass .locked renames + simulated deletes
                for target_path in created_files:
                    if target_path.exists():
                        random_payload = bytearray(random.getrandbits(8) for _ in range(4096))
                        with open(target_path, "wb") as f:
                            f.write(random_payload)
                        modified_count += 1
                        storage_monitor.process_event("modified", str(target_path))
                        time.sleep(0.02)

                time.sleep(0.08)
                self._emit_progress(simulation_id, normalized_intensity, "DETECTION_ANALYSIS", 75)

                # Mass rename with .locked extension
                for target_path in created_files[:12]:
                    if target_path.exists():
                        new_path = target_path.with_name(f"{target_path.name}.locked")
                        for _ in range(5):
                            try:
                                if new_path.exists():
                                    new_path.unlink()
                                target_path.rename(new_path)
                                renamed_files.append(new_path)
                                storage_monitor.process_event("renamed", str(new_path), old_path=str(target_path))
                                break
                            except (PermissionError, OSError):
                                time.sleep(0.05)
                        time.sleep(0.02)

                # Rapid deletion of 4 test files to demonstrate data destruction heuristic
                for target_path in created_files[12:16]:
                    if target_path.exists():
                        try:
                            target_path.unlink()
                            deleted_count += 1
                            storage_monitor.process_event("deleted", str(target_path))
                            time.sleep(0.02)
                        except OSError:
                            pass

            total_events_generated = len(created_files) + modified_count + len(renamed_files) + deleted_count
            self._emit_progress(simulation_id, normalized_intensity, "COMPLETED", 100)

            # Audit: Record simulation completion
            audit_service.log_event(
                event_type="simulation_completed",
                action="Complete Defensive Simulation",
                result="SUCCESS",
                severity="INFO" if normalized_intensity == "LOW" else ("WARNING" if normalized_intensity == "MEDIUM" else "CRITICAL"),
                source="safe_simulator",
                related_entity_id=simulation_id,
                details=f"Simulation {simulation_id} ({normalized_intensity}) generated {total_events_generated} events across {len(created_files)} files. Expected risk: {expected_risk}"
            )

            logger.info("Safe simulation %s completed: %d created, %d modified, %d renamed, %d deleted.",
                        simulation_id, len(created_files), modified_count, len(renamed_files), deleted_count)

            return {
                "success": True,
                "simulation_id": simulation_id,
                "intensity": normalized_intensity,
                "sandbox_path": str(self.demo_dir),
                "sandbox_directory": str(self.demo_dir),
                "files_simulated": len(created_files),
                "files_created": len(created_files),
                "files_modified": modified_count,
                "files_renamed": len(renamed_files),
                "files_deleted": deleted_count,
                "events_generated": total_events_generated,
                "expected_risk_level": expected_risk,
                "status": "COMPLETED",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actions": [
                    f"Created {len(created_files)} synthetic demonstration documents in demo sandbox",
                    f"Generated {modified_count} controlled modifications ({'benign plain text' if normalized_intensity == 'LOW' else 'simulated high-entropy entropy spikes'})",
                    f"Executed {len(renamed_files)} simulated extension alterations ({'.locked'})" if renamed_files else "No extension alterations (LOW intensity)",
                    f"Executed {deleted_count} controlled file deletions" if deleted_count else "Zero file deletions (harmless retention)",
                ],
                "message": f"Safe {normalized_intensity} simulation completed successfully within demo sandbox."
            }

        except Exception as e:
            logger.error("Simulation error in %s: %s", simulation_id, e)
            audit_service.log_event(
                event_type="simulation_failed",
                action="Execute Defensive Simulation",
                result="FAILED",
                severity="WARNING",
                source="safe_simulator",
                related_entity_id=simulation_id,
                details=f"Simulation error: {e}"
            )
            return {
                "success": False,
                "simulation_id": simulation_id,
                "intensity": normalized_intensity,
                "error": str(e),
                "status": "FAILED",
                "message": f"Simulation interrupted: {e}"
            }
        finally:
            self.is_running = False
            self._cancel_requested = False

    def cleanup_demo_folder(self, custom_path: Optional[str] = None) -> Dict[str, Any]:
        """Cleans up temporary simulation files strictly from protected_storage/demo/."""
        target_dir = Path(custom_path).resolve() if custom_path else self.demo_dir

        # Strict Sandbox Enforcement Check
        if not self.validate_sandbox_path(target_dir):
            err_msg = f"Security Violation: Target path '{custom_path}' is outside authorized sandbox '{self.demo_dir}'. Arbitrary path traversal is strictly prohibited."
            logger.error(err_msg)
            raise ValueError(err_msg)

        if not target_dir.exists():
            return {
                "success": True,
                "sandbox_directory": str(self.demo_dir),
                "removed_count": 0,
                "message": "Demo sandbox is already clean."
            }

        removed = 0
        for item in target_dir.iterdir():
            # Security Rule: NEVER delete subdirectories, snapshots, or parent directory
            if item.is_file():
                # Double-check file is inside demo_dir
                if item.resolve().parent == self.demo_dir:
                    try:
                        item.unlink()
                        removed += 1
                    except Exception as e:
                        logger.warning("Could not delete sandbox artifact %s: %s", item, e)

        # Audit: Record cleanup
        audit_service.log_event(
            event_type="simulation_cleaned",
            action="Clean Simulation Sandbox",
            result="SUCCESS",
            severity="INFO",
            source="safe_simulator",
            related_entity_id=str(self.demo_dir),
            details=f"Removed {removed} temporary demonstration artifacts from sandbox"
        )

        logger.info("Cleaned %d temporary simulation files from %s", removed, self.demo_dir)
        return {
            "success": True,
            "sandbox_directory": str(self.demo_dir),
            "removed_count": removed,
            "message": f"Successfully cleaned {removed} temporary simulation artifacts from demo sandbox."
        }


# Global Safe Simulator singleton
safe_simulator = SafeRansomwareSimulator()

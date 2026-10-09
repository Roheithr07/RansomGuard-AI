"""RansomGuard AI - Recovery Pydantic Models."""
from typing import Optional, List
from pydantic import BaseModel, Field


class RecoveryRequest(BaseModel):
    snapshot_id: str = Field(..., description="Unique ID of snapshot to restore from")
    target_directory: Optional[str] = None
    confirm: bool = Field(False, description="Explicit confirmation required to restore")


class RecoveryResponse(BaseModel):
    recovery_id: str
    snapshot_id: str
    safety_snapshot_id: Optional[str] = None
    status: str
    restored_files_count: int
    restored_bytes: int
    verification_result: Optional[str] = None
    started_at: str
    completed_at: Optional[str]
    message: str
    details: Optional[str] = ""


class RecoveryPreviewResponse(BaseModel):
    snapshot_id: str
    file_count: int
    total_size_bytes: int
    integrity_valid: bool
    files_to_restore: List[str]
    warning: Optional[str] = None

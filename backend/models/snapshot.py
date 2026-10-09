"""RansomGuard AI - Snapshot Pydantic Models."""
from typing import Optional, List
from pydantic import BaseModel, Field


class SnapshotCreateRequest(BaseModel):
    description: Optional[str] = "Manual snapshot checkpoint"


class SnapshotFileItem(BaseModel):
    relative_path: str
    file_size: int
    sha256_hash: str
    modified_at: str


class SnapshotResponse(BaseModel):
    id: int
    snapshot_id: str
    created_at: str
    file_count: int
    total_size_bytes: int
    snapshot_path: str
    integrity_hash: str
    integrity_status: str
    description: str
    recovery_available: bool

    class Config:
        from_attributes = True


class SnapshotVerifyResponse(BaseModel):
    snapshot_id: str
    verified: bool
    integrity_status: str
    checked_files: int
    corrupted_files: List[str] = []
    message: str

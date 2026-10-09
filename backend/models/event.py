"""RansomGuard AI - Event Pydantic Models."""
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class FileEventBase(BaseModel):
    event_type: str = Field(..., description="File operation: created, modified, deleted, renamed, moved")
    file_path: str
    file_name: str
    extension: Optional[str] = ""
    file_size: Optional[int] = 0
    entropy: Optional[float] = 0.0
    process_id: Optional[int] = None
    process_name: Optional[str] = None
    risk_score: Optional[int] = 0
    severity: Optional[str] = "INFO"
    detection_reasons: Optional[List[str]] = []
    status: Optional[str] = "recorded"


class FileEventCreate(FileEventBase):
    pass


class FileEventResponse(FileEventBase):
    id: int
    event_id: str
    timestamp: str

    class Config:
        from_attributes = True

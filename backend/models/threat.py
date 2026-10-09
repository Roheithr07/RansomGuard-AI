"""RansomGuard AI - Threat Pydantic Models."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ThreatBase(BaseModel):
    severity: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    risk_score: int = Field(..., ge=0, le=100)
    detection_reasons: List[str]
    affected_files: List[str]
    file_count: Optional[int] = 1
    process_info: Optional[Dict[str, Any]] = {}
    status: Optional[str] = "Detected"


class ThreatStatusUpdate(BaseModel):
    status: str = Field(..., description="Detected, Investigating, Contained, Resolved")


class ThreatResponse(ThreatBase):
    id: int
    threat_id: str
    timestamp: str
    resolved_at: Optional[str] = None

    class Config:
        from_attributes = True

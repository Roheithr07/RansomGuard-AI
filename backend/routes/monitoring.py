"""Monitoring Route Handlers Module.

Provides API endpoints for managing protected folders, checking file monitor status,
and querying real-time telemetry metrics.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def get_monitoring_status():
    """Get current status of file system and system monitoring."""
    return {"status": "idle", "active_monitors": 0}

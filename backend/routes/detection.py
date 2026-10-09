"""Detection Route Handlers Module.

Provides API endpoints for inspecting AI detection model status, anomaly scores,
and security alert histories.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def get_detection_status():
    """Get current status of AI risk evaluation engine."""
    return {"status": "ready", "models_loaded": False, "threat_level": "LOW"}

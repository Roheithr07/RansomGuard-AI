"""RansomGuard AI - Snapshots & Backups API Router.

Provides immutable backup point creation, SHA-256 integrity verification,
snapshot catalog listing, and snapshot deletion endpoints.
"""
from fastapi import APIRouter, HTTPException
from backend.services.snapshot_manager import snapshot_manager
from backend.models.snapshot import SnapshotCreateRequest, SnapshotVerifyResponse

router = APIRouter()


@router.get("/snapshots")
def list_snapshots():
    """Lists all available storage snapshots and recovery points."""
    snapshots = snapshot_manager.list_snapshots()
    valid_count = sum(1 for s in snapshots if s["integrity_status"] == "Valid")
    total_volume = sum(s["total_size_bytes"] for s in snapshots)
    recovery_count = sum(1 for s in snapshots if s.get("recovery_available"))

    return {
        "count": len(snapshots),
        "total_snapshots": len(snapshots),
        "valid_snapshots": valid_count,
        "total_volume_bytes": total_volume,
        "recovery_ready_count": recovery_count,
        "snapshots": snapshots
    }






@router.post("/snapshots")
@router.post("/snapshots/create")
def create_snapshot(request: SnapshotCreateRequest):
    """Creates a new immutable snapshot of the protected storage directory."""
    try:
        new_snap = snapshot_manager.create_snapshot(description=request.description or "Manual storage checkpoint")
        return {
            "success": True,
            "snapshot": new_snap,
            "message": f"Snapshot '{new_snap['snapshot_id']}' created successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create snapshot: {e}")


@router.post("/snapshots/verify/{snapshot_id}")
def verify_snapshot(snapshot_id: str):
    """Cryptographically verifies SHA-256 integrity of snapshot files against manifest."""
    result = snapshot_manager.verify_snapshot(snapshot_id)
    if result["integrity_status"] == "NotFound":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.delete("/snapshots/{snapshot_id}")
def delete_snapshot(snapshot_id: str):
    """Safely deletes a snapshot point if not currently locked."""
    success, message = snapshot_manager.delete_snapshot(snapshot_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message}

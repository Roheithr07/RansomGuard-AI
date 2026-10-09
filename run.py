"""RansomGuard AI - Main Server Entry Point.

Initializes the FastAPI application with real-time filesystem monitoring,
risk evaluation engine, SQLite database, and WebSocket event telemetry.
"""
import os
import sys
import uvicorn
from backend.core.config import API_HOST, API_PORT


def main():
    """Launch the RansomGuard AI FastAPI backend server."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 70)
    print(" [*] RansomGuard AI - AI-Powered Ransomware Detection & Storage Protection")
    print("=" * 70)
    print(f" * Dashboard UI:      http://localhost:{API_PORT}/")
    print(f" * OpenAPI Docs:      http://localhost:{API_PORT}/docs")
    print(f" * ReDoc Specs:       http://localhost:{API_PORT}/redoc")
    print(f" * WebSocket Stream:  ws://localhost:{API_PORT}/ws/monitor")
    print("=" * 70)
    print(f"Starting server on http://{API_HOST}:{API_PORT} ... (Press Ctrl+C to stop)")

    uvicorn.run(
        "backend.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
    )


if __name__ == "__main__":
    main()

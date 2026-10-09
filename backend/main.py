"""RansomGuard AI - Main FastAPI Application.

AI-Powered Ransomware Detection and Storage Protection System.
Integrates real-time filesystem watchdog monitoring, explainable risk engine,
cryptographic snapshot management, safe recovery, and WebSocket live event telemetry.
"""
import asyncio
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.core.config import (
    BASE_DIR,
    PROTECTED_DIRECTORY,
    SNAPSHOT_DIRECTORY,
    MONITOR_ENABLED,
)
from backend.core.database import init_database
from backend.core.websocket import ws_manager
from backend.services.storage_monitor import storage_monitor
from backend.services.snapshot_manager import snapshot_manager

# API Routers
from backend.api import (
    dashboard,
    monitoring,
    storage,
    threats,
    snapshots,
    recovery,
    ai_analysis,
    reports,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ransomguard.main")


def seed_protected_storage_if_empty():
    """Seeds benign sample business documents into protected_storage if it is completely empty."""
    PROTECTED_DIRECTORY.mkdir(parents=True, exist_ok=True)
    existing_files = list(PROTECTED_DIRECTORY.glob("*.*"))
    if not existing_files:
        sample_files = {
            "quarterly_financial_report.xlsx": "Q1 Revenue: $1,250,000 | Operational Costs: $820,000 | Net Profit: $430,000\n",
            "corporate_strategy_2026.docx": "Confidential Corporate Roadmap for Enterprise Storage Security & Threat Mitigation.\n",
            "customer_database_export.csv": "id,name,email,tier\n1,Alice Smith,alice@example.com,Enterprise\n2,Bob Jones,bob@example.com,Standard\n",
            "system_architecture_notes.txt": "RansomGuard AI defensive architecture with zero-trust snapshot recovery verification.\n",
        }
        for fname, content in sample_files.items():
            fpath = PROTECTED_DIRECTORY / fname
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
        logger.info("Seeded initial benign test documents into %s", PROTECTED_DIRECTORY)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown sequences."""
    logger.info("Initializing RansomGuard AI subsystem...")

    # 1. Initialize SQLite Database
    init_database()

    # 2. Seed initial storage documents
    seed_protected_storage_if_empty()

    # 3. Attach current event loop to storage monitor for WebSocket event dispatching
    loop = asyncio.get_running_loop()
    storage_monitor.set_event_loop(loop)

    # 4. Create initial baseline snapshot if none exists
    existing_snapshots = snapshot_manager.list_snapshots()
    if not existing_snapshots:
        try:
            snapshot_manager.create_snapshot(description="Initial System Baseline Snapshot")
            logger.info("Created baseline system snapshot.")
        except Exception as e:
            logger.warning("Could not create initial snapshot: %s", e)

    # 5. Start real-time watchdog filesystem monitor
    if MONITOR_ENABLED:
        storage_monitor.start()

    logger.info("RansomGuard AI is fully operational and listening.")
    yield

    # Shutdown
    logger.info("Shutting down RansomGuard AI services...")
    storage_monitor.stop()
    logger.info("All monitoring services suspended.")


app = FastAPI(
    title="RansomGuard AI - Storage Protection API",
    description="AI-powered defensive ransomware detection, explainable risk scoring, and verified storage snapshot recovery.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend dashboard communication (Vite & local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(monitoring.router, prefix="/api", tags=["Monitoring & Events"])
app.include_router(storage.router, prefix="/api", tags=["Storage Telemetry"])
app.include_router(threats.router, prefix="/api", tags=["Threat Intelligence"])
app.include_router(snapshots.router, prefix="/api", tags=["Snapshots & Backups"])
app.include_router(recovery.router, prefix="/api", tags=["Recovery & Restores"])
app.include_router(ai_analysis.router, prefix="/api", tags=["AI & Risk Analysis"])
app.include_router(reports.router, prefix="/api", tags=["Reports & Audit"])


@app.websocket("/ws/monitor")
async def websocket_monitor_endpoint(websocket: WebSocket):
    """Real-time WebSocket event streaming endpoint for the dashboard."""
    await ws_manager.connect(websocket)
    try:
        # Send initial welcome & state snapshot
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "message": "Connected to RansomGuard AI real-time telemetry stream.",
            "metrics": storage_monitor.get_current_metrics()
        })
        while True:
            # Keep connection open and receive potential client pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.debug("WebSocket exception: %s", e)
        ws_manager.disconnect(websocket)


# Serve Permanent Frontend: RansomGuard-Dashboard.html
FRONTEND_HTML_PATH = BASE_DIR / "frontend" / "RansomGuard-Dashboard.html"


@app.get("/")
def serve_dashboard_root():
    """Serves the permanent Apple-inspired RansomGuard Dashboard."""
    if FRONTEND_HTML_PATH.exists():
        return FileResponse(str(FRONTEND_HTML_PATH))
    return {
        "system": "RansomGuard AI Storage Protection Engine",
        "status": "operational",
        "api_docs": "/docs",
        "message": "Frontend file RansomGuard-Dashboard.html not found in /frontend directory."
    }


@app.get("/dashboard")
@app.get("/live-monitor")
@app.get("/monitor")
@app.get("/threats")
@app.get("/storage")
@app.get("/backups")
@app.get("/recovery")
@app.get("/ai-analysis")
@app.get("/reports")
@app.get("/settings")
def serve_dashboard_alias():
    """Alias routes to serve the permanent RansomGuard Dashboard."""
    return serve_dashboard_root()


@app.get("/api/health")
def api_health():
    """Backend Health Check."""
    return {
        "system": "RansomGuard AI Storage Protection Engine",
        "status": "operational",
        "active_frontend": "RansomGuard-Dashboard.html",
        "monitoring": storage_monitor.is_running
    }


# Mount frontend static assets if needed
FRONTEND_DIR = BASE_DIR / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

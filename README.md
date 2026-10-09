# RansomGuard AI — AI-Powered Ransomware Detection and Storage Protection System

> **RansomGuard AI** is a defense-in-depth, ransomware-resilient intelligent storage monitoring and recovery system. It combines real-time filesystem activity surveillance (via Watchdog), an explainable behavioral risk engine (Shannon entropy profiling, mutation detection, and burst rate telemetry), immutable SHA-256 snapshot checkpoints, and safe point-in-time disaster recovery.

---

## 🎨 Approved Liquid Glass Frontend

The approved frontend is available directly at:
```
frontend/RansomGuard-Dashboard.html
```
It utilizes an Apple-inspired liquid glass / glassmorphism interface featuring:
- **RansomGuard AI** branding with light blue / white glass aesthetics and animated ambient background blobs
- **Sidebar Navigation**: Dashboard, Live Monitor, Threats, Storage, Backup & Snapshots, Recovery, AI Analysis, Reports, and Settings
- **Live WebSocket Streaming**: Connects automatically to `ws://localhost:8000/ws/monitor` with instant re-connect
- **Interactive REST Integrations**: Real-time event charts, threat incident containment, snapshot creation, SHA-256 verification, one-click safe attack simulation, and disaster recovery rollback

---

## 🏗️ Project Architecture

```
RansomGuard/
├── frontend/
│   └── RansomGuard-Dashboard.html   # Approved liquid-glass frontend with WebSocket & REST API hooks
│
├── backend/
│   ├── main.py                      # FastAPI server with CORS, WebSockets, Lifespan, and static routes
│   ├── requirements.txt             # Backend dependencies manifest
│   │
│   ├── api/                         # Modular REST API endpoints
│   │   ├── dashboard.py             # GET /api/dashboard
│   │   ├── monitoring.py            # GET /api/events, POST /api/monitor/start, POST /api/monitor/stop, POST /api/demo/simulate
│   │   ├── threats.py               # GET /api/threats, PATCH /api/threats/{id}/status
│   │   ├── storage.py               # GET /api/storage, POST /api/storage/configure
│   │   ├── snapshots.py             # GET /api/snapshots, POST /api/snapshots/create, POST /api/snapshots/verify/{id}
│   │   ├── recovery.py              # GET /api/recovery, POST /api/recovery/restore, GET /api/recovery/preview/{id}
│   │   ├── ai_analysis.py           # GET /api/ai-analysis
│   │   └── reports.py               # GET /api/reports, GET /api/reports/export
│   │
│   ├── core/
│   │   ├── config.py                # Environment-driven configuration and risk thresholds
│   │   ├── database.py              # SQLite schemas with indexing (events, threats, snapshots, recovery)
│   │   └── websocket.py             # Active connection manager and live telemetry broadcast
│   │
│   ├── models/                      # Pydantic schemas for request/response validation
│   │   ├── event.py
│   │   ├── threat.py
│   │   ├── snapshot.py
│   │   └── recovery.py
│   │
│   ├── services/                    # Core defensive security business logic
│   │   ├── storage_monitor.py       # Python watchdog filesystem surveillance engine
│   │   ├── ransomware_detector.py   # Hybrid behavioral detector & ML feature vector extractor
│   │   ├── risk_engine.py           # Shannon entropy, burst window tracking, and explainable 0-100 scoring
│   │   ├── snapshot_manager.py      # Immutable directory snapshots and cryptographic SHA-256 validation
│   │   ├── recovery_manager.py      # Pre-flight checked disaster rollback and audit logging
│   │   ├── process_monitor.py       # Safe psutil process inspection
│   │   └── simulator.py             # Safe, sandboxed attack simulation inside protected_storage/demo/
│   │
│   └── database/
│       └── ransomguard.db           # SQLite database storing events, threats, manifests, and audit history
│
├── protected_storage/               # Monitored directory containing protected files
│   └── demo/                        # Sandboxed folder for harmless demonstration attack simulation
│
├── snapshots/                       # Immutable local backup snapshots repository
├── logs/                            # Application and telemetry logs
├── .env.example                     # Environment configuration template
├── README.md                        # Documentation and demonstration guide
└── run.py                           # CLI entry point to start the server
```

---

## ⚡ Quick Start & Running Instructions

### 1. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Launch the Server

Run using the entry point:
```bash
python run.py
```
Or start via `uvicorn`:
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Accessing the System

| Interface | URL | Description |
| :--- | :--- | :--- |
| **Liquid Glass Dashboard** | [http://localhost:8000/](http://localhost:8000/) | Approved Apple-style liquid glass interface |
| **Interactive API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger UI for testing all REST endpoints |
| **ReDoc Documentation** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | Alternative OpenAPI documentation |
| **WebSocket Feed** | `ws://localhost:8000/ws/monitor` | Real-time filesystem and alert stream |

> **Direct HTML Access:** You can also double-click [frontend/RansomGuard-Dashboard.html](frontend/RansomGuard-Dashboard.html) directly in any modern browser. It will connect to the backend running at `http://localhost:8000`.

---

## 🛡️ Core Capabilities & Endpoints

### 1. Real-Time Storage Monitoring (Watchdog)
Monitors `protected_storage/` recursively for:
- File Created
- File Modified
- File Deleted
- File Moved / Renamed

Every operation records event ID, timestamp, file path, size, Shannon entropy, process context, risk score, and status into SQLite.

### 2. Explainable Ransomware Risk Engine
Evaluates telemetry across 8 behavioral dimensions:
1. **Shannon Entropy Spike**: Measures information randomness (0.00 to 8.00 bits/byte). Plain text ~3.5-5.0, whereas encrypted ciphertext reaches 7.5-8.0.
2. **Mass Modification Bursts**: Flags excessive write volume in sliding 10-second windows.
3. **Mass Renaming / Mutating**: Detects bulk extension alterations.
4. **Known Ransomware Extensions**: Flags patterns like `.locked`, `.crypto`, `.enc`, `.crypted`, `.wnry`.
5. **Abnormal Operations/Second**: Identifies non-human disk activity.

**Risk Levels:**
- `0 – 29`: **LOW** (Standard filesystem operations)
- `30 – 59`: **MEDIUM** (Elevated write frequencies)
- `60 – 79`: **HIGH** (Suspect mutation or burst anomaly)
- `80 – 100`: **CRITICAL** (Active ransomware behavioral signature)

### 3. Safe Sandboxed Demonstration Mode
To safely demonstrate ransomware detection without damaging user or system files:
```http
POST /api/demo/simulate?intensity=medium
```
- Operates **exclusively** inside `protected_storage/demo/`
- Creates harmless test documents (e.g. `.docx`, `.xlsx`, `.pdf`)
- Injects high-entropy pseudo-random bytes simulating encryption
- Appends `.locked` in rapid bursts
- Watchdog catches the activity in real-time -> RiskEngine evaluates score -> Dashboard sounds visual alarm -> Threat incident is logged.

### 4. Cryptographic Snapshots & Verified Recovery
- **Snapshot Creation (`POST /api/snapshots/create`)**: Copies protected files to `snapshots/snap_<timestamp>/`, computing SHA-256 signatures for every file and a master manifest.
- **Integrity Verification (`POST /api/snapshots/verify/{id}`)**: Cryptographically validates current disk bytes against stored signatures.
- **Safe Disaster Recovery (`POST /api/recovery/restore`)**: Previews files, verifies integrity, restores files to protected storage, and records audit trail.

---

## 🧪 Testing and Verification Guide

### Test 1: Health & Dashboard Telemetry
```bash
curl http://localhost:8000/api/dashboard
```
*Expected Result:* Returns JSON containing files monitored, threats detected, storage health %, latest snapshot, and recent events.

### Test 2: Trigger Safe Ransomware Simulation
```bash
curl -X POST "http://localhost:8000/api/demo/simulate?intensity=medium"
```
*Expected Result:* Creates benign test files inside `protected_storage/demo/`, modifies them with high entropy, and renames them to `.locked`. The dashboard immediately updates and flashes a high-risk alert.

### Test 3: Check Threat Center
```bash
curl http://localhost:8000/api/threats
```
*Expected Result:* Lists the incident generated by the simulation with severity, risk score, detection reasons, and affected files.

### Test 4: Create a Storage Snapshot
```bash
curl -X POST http://localhost:8000/api/snapshots/create -H "Content-Type: application/json" -d "{\"description\": \"Baseline Pre-Attack Checkpoint\"}"
```
*Expected Result:* Creates an immutable snapshot with unique ID and SHA-256 manifest.

### Test 5: Verify and Restore
```bash
curl -X POST http://localhost:8000/api/recovery/restore -H "Content-Type: application/json" -d "{\"snapshot_id\": \"<YOUR_SNAPSHOT_ID>\", \"confirm\": true}"
```
*Expected Result:* Validates SHA-256 hashes, safely restores files to `protected_storage/`, and returns `status: "SUCCESS"`.

---

## 🔒 Defensive Security Posture

RansomGuard AI is strictly an **educational and enterprise defensive tool**:
- Does **not** contain real malware, self-propagation, destructive encryption, or privilege escalation.
- Safe simulation is strictly sandboxed to `protected_storage/demo/`.
- All restorations require explicit confirmation and cryptographic validation.

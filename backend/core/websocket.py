"""RansomGuard AI - WebSocket Connection Manager.

Maintains active browser connections for real-time filesystem event telemetry,
threat detection alerts, and storage activity updates.
"""
import json
import logging
from typing import Set, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger("ransomguard.websocket")


class ConnectionManager:
    """Manages active WebSocket connections and broadcasting."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        """Accepts and registers a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info("WebSocket client connected. Total active: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        """Removes a disconnected WebSocket from active pool."""
        self.active_connections.discard(websocket)
        logger.info("WebSocket client disconnected. Remaining active: %d", len(self.active_connections))

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcasts a JSON-serializable message payload to all active clients."""
        if not self.active_connections:
            return

        payload = json.dumps(message)
        dead_connections = set()

        for connection in list(self.active_connections):
            try:
                await connection.send_text(payload)
            except Exception as e:
                logger.warning("Error sending message to client: %s", e)
                dead_connections.add(connection)

        for dead in dead_connections:
            self.disconnect(dead)


# Global WebSocket Manager singleton
ws_manager = ConnectionManager()

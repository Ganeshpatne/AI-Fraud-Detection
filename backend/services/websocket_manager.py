"""
WebSocket connection manager for real-time fraud alerts and activity stream.
"""
import json
import logging
from datetime import datetime
from typing import Dict, Set
from fastapi import WebSocket

logger = logging.getLogger("fraud_detection.alerts")


class ConnectionManager:
    """Manage WebSocket connections for real-time fraud alerts."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.alert_history: list[dict] = []
        self.max_history = 100

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket client connected. Total: %d", len(self.active_connections))

        # Send recent alert history to newly connected client
        if self.alert_history:
            await websocket.send_json({
                "type": "history",
                "data": self.alert_history[-20:],  # last 20 alerts
            })

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("WebSocket client disconnected. Total: %d", len(self.active_connections))

    async def broadcast_alert(self, alert_data: dict):
        """Broadcast a fraud alert to all connected clients."""
        message = {
            "type": "fraud_alert",
            "data": alert_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Store in history
        self.alert_history.append(message)
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]

        # Broadcast
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # Cleanup dead connections
        for conn in disconnected:
            self.disconnect(conn)

        logger.info("Alert broadcast to %d clients", len(self.active_connections))

    async def broadcast_activity(self, activity_data: dict):
        """Broadcast a general activity event."""
        message = {
            "type": "activity",
            "data": activity_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)


# Singleton
ws_manager = ConnectionManager()

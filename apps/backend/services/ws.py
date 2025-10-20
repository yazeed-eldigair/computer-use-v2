import json
from typing import Dict, Set

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class WebSocketManager:
    def __init__(self):
        # Map of session_id to set of connected WebSocket clients
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a new WebSocket client"""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        """Disconnect a WebSocket client"""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast_to_session(self, session_id: str, message: dict):
        """Broadcast a message to all clients in a session"""
        if session_id not in self.active_connections:
            return

        # Convert message to JSON string
        json_message = json.dumps(message)

        # Send to all connected clients for this session
        for connection in self.active_connections[session_id]:
            try:
                await connection.send_text(json_message)
            except (WebSocketDisconnect, RuntimeError) as e:
                # Handle WebSocket disconnection and runtime errors
                print(f"WebSocket error for session {session_id}: {str(e)}")
                self.disconnect(connection, session_id)

    async def broadcast_file_update(
        self, session_id: str, action: str, file_id: str
    ):
        """Broadcast a file update"""
        await self.broadcast_to_session(
            session_id,
            {"type": "file_update", "action": action, "file_id": file_id},
        )


ws_manager = WebSocketManager()

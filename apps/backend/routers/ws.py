from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.ws import ws_manager

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for receiving real-time updates.

    Clients will receive updates for:
    - File uploads and deletions
    - Task status changes
    - Claude messages
    - Session updates

    Args:
        websocket: The WebSocket connection
        session_id: The ID of the session to subscribe to
    """
    await ws_manager.connect(websocket, session_id)
    try:
        while True:
            # Wait for messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, session_id)

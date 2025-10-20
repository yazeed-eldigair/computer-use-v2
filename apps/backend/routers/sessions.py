from typing import List

from fastapi import APIRouter, HTTPException
from models.base import Session
from pydantic import BaseModel
from services.session import SessionService


class SessionCreate(BaseModel):
    title: str


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=Session, summary="Create a new session")
async def create_session(data: SessionCreate):
    """Create a new session with the given title.

    Args:
        data: The session creation data containing the title

    Returns:
        Session: The created session object
    """
    return SessionService.create_session(data.title)


@router.get("", response_model=List[Session], summary="List all sessions")
async def list_sessions():
    """Get a list of all sessions.

    Returns:
        List[Session]: List of all sessions
    """
    return SessionService.list_sessions()


@router.get(
    "/{session_id}", response_model=Session, summary="Get a session by ID"
)
async def get_session(session_id: str):
    """Get a session by its ID.

    Args:
        session_id: The ID of the session

    Returns:
        Session: The session object

    Raises:
        HTTPException: If session is not found
    """
    session = SessionService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.patch(
    "/{session_id}", response_model=Session, summary="Update a session"
)
async def update_session(
    session_id: str, title: str = None, status: str = None
):
    """Update a session's title or status.

    Args:
        session_id: The ID of the session
        title: Optional new title
        status: Optional new status

    Returns:
        Session: The updated session object

    Raises:
        HTTPException: If session is not found
    """
    session = SessionService.update_session(session_id, title, status)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/{session_id}", response_model=dict, summary="Delete a session")
async def delete_session(session_id: str):
    """Delete a session and all its associated data.

    Args:
        session_id: The ID of the session to delete

    Returns:
        dict: Success status

    Raises:
        HTTPException: If session is not found
    """
    if not SessionService.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success"}

from typing import List

from fastapi import APIRouter, HTTPException
from models.base import Message
from pydantic import BaseModel, Field
from services.chat import chat_service

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


class MessageRequest(BaseModel):
    """Request model for creating a new message."""

    content: str = Field(description="The message content to send to chat")


@router.post(
    "/{session_id}/messages",
    summary="Create a new message",
)
async def create_message(session_id: str, request: MessageRequest):
    """Send a message to chat and get its response.

    Args:
        session_id: The ID of the session
        request: The message request containing content and options

    Raises:
        HTTPException: If chat API request fails
    """
    try:
        await chat_service.create_message(
            session_id=session_id,
            userMessage=request.content,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{session_id}/messages",
    response_model=List[Message],
    summary="Get session messages",
)
async def get_session_messages(session_id: str):
    """Get all messages in a conversation session.

    Args:
        session_id: The ID of the session

    Returns:
        List[Message]: List of messages in chronological order, with content formatted for frontend
    """
    import json

    messages = await chat_service.get_session_messages(session_id)

    # Convert content blocks to string for frontend
    for msg in messages:
        msg.content = json.dumps(msg.content)

    return messages

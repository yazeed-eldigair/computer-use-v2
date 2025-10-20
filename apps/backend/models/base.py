from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class TimestampedModel(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class Session(TimestampedModel):
    id: str
    title: str
    status: str = "active"


class Message(TimestampedModel):
    id: str
    session_id: str
    role: str
    content: List[
        dict[str, Any]
    ]  # List of content blocks that can contain nested objects
    message: Optional[str] = None  # Optional human-readable message


class FileMetadata(TimestampedModel):
    id: str
    filename: str
    path: str
    mime_type: str
    size: int
    session_id: Optional[str] = None
    uploaded_at: Optional[datetime] = None


class TaskStep(TimestampedModel):
    id: str
    session_id: str
    action: str
    status: str = "pending"
    result: Optional[str] = None
    completed_at: Optional[datetime] = None

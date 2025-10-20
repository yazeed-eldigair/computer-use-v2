import logging
import uuid
from datetime import datetime
from typing import List, Optional

from models.base import Message, Session
from utils.database import execute_query

logger = logging.getLogger(__name__)


class SessionService:
    @staticmethod
    def create_session(title: str) -> Session:
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()

        execute_query(
            """
            INSERT INTO sessions (id, title, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, title, "active", now, now),
        )

        return Session(
            id=session_id,
            title=title,
            created_at=now,
            updated_at=now,
            status="active",
        )

    @staticmethod
    def get_session(session_id: str) -> Optional[Session]:
        result = execute_query(
            "SELECT * FROM sessions WHERE id = ?", (session_id,)
        )

        if not result:
            return None

        session = result[0]
        return Session(
            id=session["id"],
            title=session["title"],
            created_at=session["created_at"],
            updated_at=session["updated_at"],
            status=session["status"],
        )

    @staticmethod
    def save_message(
        session_id: str,
        role: str,
        content: list[dict] | str,
        message: str | None = None,
    ) -> str:
        """Save a message to the database.

        Args:
            session_id: The ID of the session
            role: The role (user/assistant)
            content: Content block dict or string to convert to text block
            message: Human-readable message text

        Returns:
            str: The ID of the created message
        """
        import json

        msg_id = str(uuid.uuid4())

        # Convert string content to a text block array
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]

        content_json = json.dumps(content)

        execute_query(
            """
            INSERT INTO messages (id, session_id, role, content, message, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                msg_id,
                session_id,
                role,
                content_json,
                message,
                datetime.utcnow().isoformat(),
            ),
        )

        return msg_id

    @staticmethod
    def list_sessions() -> List[Session]:
        results = execute_query(
            "SELECT * FROM sessions ORDER BY created_at DESC"
        )
        return [
            Session(
                id=row["id"],
                title=row["title"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                status=row["status"],
            )
            for row in results
        ]

    @staticmethod
    def update_session(
        session_id: str, title: str = None, status: str = None
    ) -> Optional[Session]:
        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)

        if status is not None:
            updates.append("status = ?")
            params.append(status)

        if not updates:
            return None

        updates.append("updated_at = ?")
        now = datetime.utcnow()
        params.extend([now, session_id])

        query = f"""
            UPDATE sessions
            SET {", ".join(updates)}
            WHERE id = ?
        """

        execute_query(query, tuple(params))
        return SessionService.get_session(session_id)

    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete a session and all its associated data.

        Args:
            session_id: The ID of the session to delete

        Returns:
            bool: True if session was found and deleted, False otherwise
        """
        # Check if session exists
        session = SessionService.get_session(session_id)
        if not session:
            return False

        # Delete associated data
        execute_query(
            "DELETE FROM messages WHERE session_id = ?", (session_id,)
        )
        execute_query("DELETE FROM files WHERE session_id = ?", (session_id,))

        # Delete the session
        execute_query("DELETE FROM sessions WHERE id = ?", (session_id,))
        return True

    @staticmethod
    def get_session_messages(session_id: str) -> List[Message]:
        """Get all messages for a session in chronological order.

        Returns:
            List[Message]: List of messages with their content and optional message
        """
        import json

        results = execute_query(
            """
            SELECT id, session_id, role, content, message, created_at
            FROM messages
            WHERE session_id = ?
            ORDER BY created_at ASC
            """,
            (session_id,),
        )

        messages = []
        for row in results:
            try:
                content = json.loads(row["content"])
                logger.info(
                    f"Loaded content from DB: {content} (type: {type(content)})"
                )
                # If content is not a list, wrap it in one
                if not isinstance(content, list):
                    content = [content]
                messages.append(
                    Message(
                        id=row["id"],
                        session_id=row["session_id"],
                        role=row["role"],
                        content=content,
                        message=row["message"],
                        created_at=row["created_at"],
                    )
                )
            except json.JSONDecodeError:
                logger.error(f"Failed to parse content for message {row['id']}")
                continue

        return messages

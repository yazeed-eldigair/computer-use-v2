import os
import uuid
from datetime import datetime
from typing import List, Optional

from config import settings
from fastapi import UploadFile
from models.base import FileMetadata
from services.ws import ws_manager
from utils.database import execute_query

UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), settings.UPLOAD_DIR
)


class FileService:
    @staticmethod
    def ensure_upload_dir():
        """Create upload directory if it doesn't exist."""
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    @staticmethod
    async def save_file(
        file: UploadFile, session_id: Optional[str] = None
    ) -> FileMetadata:
        """Save an uploaded file and return its metadata."""
        FileService.ensure_upload_dir()

        # Generate unique ID and safe filename
        file_id = str(uuid.uuid4())
        original_name = file.filename
        file_ext = os.path.splitext(original_name)[1]
        base_name = os.path.splitext(original_name)[0]
        # Replace spaces and special chars with underscores
        safe_base_name = ''.join(c if c.isalnum() else '_' for c in base_name)
        safe_filename = f"{safe_base_name}_{file_id}{file_ext}"

        # Save file to disk
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Get file size
        file_size = os.path.getsize(file_path)

        # Record in database
        now = datetime.utcnow()
        execute_query(
            """
            INSERT INTO files (id, filename, path, mime_type, size, uploaded_at, created_at, updated_at, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                file_id,
                file.filename,
                safe_filename,
                file.content_type,
                file_size,
                now,
                now,
                None,
                session_id,
            ),
        )

        file_obj = FileMetadata(
            id=file_id,
            filename=file.filename,
            path=safe_filename,
            mime_type=file.content_type,
            size=file_size,
            uploaded_at=now,
            session_id=session_id,
        )

        # Notify via WebSocket if associated with a session
        if session_id:
            await ws_manager.broadcast_file_update(
                session_id, "upload", file_id
            )

        return file_obj

    @staticmethod
    def get_file(file_id: str) -> Optional[FileMetadata]:
        """Get file metadata by ID."""
        result = execute_query("SELECT * FROM files WHERE id = ?", (file_id,))

        if not result:
            return None

        file = result[0]
        return FileMetadata(
            id=file["id"],
            filename=file["filename"],
            path=file["path"],
            mime_type=file["mime_type"],
            size=file["size"],
            uploaded_at=file["uploaded_at"],
            session_id=file["session_id"],
            created_at=file["created_at"],
            updated_at=file["updated_at"],
        )

    @staticmethod
    def list_files(session_id: Optional[str] = None) -> List[FileMetadata]:
        """Get a list of files, optionally filtered by session."""
        query = "SELECT * FROM files"
        params = ()

        if session_id:
            query += " WHERE session_id = ?"
            params = (session_id,)

        results = execute_query(query, params)
        return [
            FileMetadata(
                id=file["id"],
                filename=file["filename"],
                path=file["path"],
                mime_type=file["mime_type"],
                size=file["size"],
                uploaded_at=file["uploaded_at"],
                session_id=file["session_id"],
                created_at=file["created_at"],
                updated_at=file["updated_at"],
            )
            for file in results
        ]

    @staticmethod
    async def delete_file(file_id: str) -> bool:
        """Delete a file and its database record"""
        # Get file info first
        file = FileService.get_file(file_id)
        if not file:
            return False

        # Delete from disk
        file_path = os.path.join(UPLOAD_DIR, file.path)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError:
            # Log error but continue to remove DB record
            print(f"Error deleting file {file_path}")

        # Delete from database
        execute_query("DELETE FROM files WHERE id = ?", (file_id,))

        # Notify via WebSocket if associated with a session
        if file.session_id:
            await ws_manager.broadcast_file_update(
                file.session_id, "delete", file_id
            )

        return True

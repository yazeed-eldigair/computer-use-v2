import os
from typing import List

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse
from models.base import FileMetadata
from services.file import UPLOAD_DIR, FileService

router = APIRouter(prefix="/files", tags=["files"])


@router.post("", response_model=FileMetadata, summary="Upload a new file")
async def upload_file(file: UploadFile, session_id: str):
    """Upload a new file and associate it with a session.

    Args:
        file: The file to upload
        session_id: Session ID to associate the file with

    Returns:
        FileMetadata: The uploaded file's metadata

    Raises:
        HTTPException: If no session_id is provided
    """
    if not session_id:
        raise HTTPException(
            status_code=400, detail="A session ID is required to upload files"
        )
    return await FileService.save_file(file, session_id)


@router.get(
    "",
    response_model=List[FileMetadata],
    summary="List session files"
)
async def list_files(session_id: str):
    """Get a list of all files, optionally filtered by session.

    Args:
        session_id: Optional session ID to filter files by

    Returns:
        List[FileMetadata]: List of file metadata
    """
    return FileService.list_files(session_id)


@router.get(
    "/{file_id}", response_model=FileMetadata, summary="Get file metadata"
)
async def get_file_info(file_id: str):
    """Get metadata for a specific file.

    Args:
        file_id: The ID of the file

    Returns:
        FileMetadata: The file's metadata

    Raises:
        HTTPException: If file is not found
    """
    file = FileService.get_file(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file


@router.get("/{file_id}/download", summary="Download a file")
async def download_file(file_id: str):
    """Download a specific file.

    Args:
        file_id: The ID of the file to download

    Returns:
        FileResponse: The file content with proper headers

    Raises:
        HTTPException: If file is not found
    """
    file = FileService.get_file(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = os.path.join(UPLOAD_DIR, file.path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        file_path, filename=file.filename, media_type=file.mime_type
    )


@router.delete("/{file_id}", summary="Delete a file")
async def delete_file(file_id: str):
    """Delete a specific file.

    Args:
        file_id: The ID of the file to delete

    Returns:
        dict: Success status

    Raises:
        HTTPException: If file is not found
    """
    if not await FileService.delete_file(file_id):
        raise HTTPException(status_code=404, detail="File not found")
    return {"status": "success"}

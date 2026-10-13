"""
File management routes for JARVIS / Liseth with strict path traversal protections.
"""
import os
import re
import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.auth import require_auth
from app.core.database import get_db
from app.core.models import UploadedFile

router = APIRouter(prefix="/api", tags=["files"])


def sanitize_filename(filename: str) -> str:
    """Removes path traversal components and unsafe characters."""
    filename = Path(filename).name
    # Keep alphanumeric, dots, underscores, dashes
    filename = re.sub(r"[^\w\.-]", "_", filename)
    return filename or "unnamed_file"


def verify_path_safe(target_path: Path, allowed_root: Path) -> Path:
    """
    Ensures target_path is strictly within allowed_root using resolve() and is_relative_to().
    Prevents path traversal vulnerabilities.
    """
    resolved_root = allowed_root.resolve()
    resolved_target = target_path.resolve()

    if not resolved_target.is_relative_to(resolved_root):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Acceso denegado: Intento de evasión de ruta (Path Traversal detectado)."
        )
    return resolved_target


class SaveFileRequest(BaseModel):
    filename: str
    content: str


@router.post("/upload")
async def upload_file(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Uploads a file into uploads/ safely, supporting both JSON base64 and multipart uploads.
    """
    import base64
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        body = await request.json()
        raw_name = body.get("name", "upload.bin")
        file_type = body.get("type", "application/octet-stream")
        b64_data = body.get("data", "")
        if "," in b64_data:
            b64_data = b64_data.split(",", 1)[1]
        try:
            content = base64.b64decode(b64_data)
        except Exception:
            raise HTTPException(status_code=400, detail="Formato base64 inválido")

        safe_name = sanitize_filename(raw_name)
        file_id = str(uuid.uuid4())
        stored_name = f"{file_id[:8]}_{safe_name}"
        target_path = settings.UPLOADS_DIR / stored_name
        verify_path_safe(target_path, settings.UPLOADS_DIR)

        with open(target_path, "wb") as f:
            f.write(content)

        uploaded = UploadedFile(
            id=file_id,
            name=stored_name,
            original_name=raw_name,
            size=len(content),
            file_type=file_type,
            url=f"/api/files/{stored_name}",
            file_path=str(target_path),
        )
        db.add(uploaded)
        await db.commit()

        return {
            "success": True,
            "file": {
                "id": file_id,
                "name": stored_name,
                "originalName": raw_name,
                "size": len(content),
                "type": file_type,
                "url": f"/api/files/{stored_name}",
            }
        }

    # Multipart form upload
    form = await request.form()
    file = form.get("file")
    if not file:
        raise HTTPException(status_code=400, detail="No se envió ningún archivo")

    safe_name = sanitize_filename(getattr(file, "filename", "upload.bin"))
    file_id = str(uuid.uuid4())
    stored_name = f"{file_id[:8]}_{safe_name}"
    target_path = settings.UPLOADS_DIR / stored_name
    verify_path_safe(target_path, settings.UPLOADS_DIR)

    content = await file.read()
    with open(target_path, "wb") as f:
        f.write(content)

    uploaded = UploadedFile(
        id=file_id,
        name=stored_name,
        original_name=getattr(file, "filename", safe_name),
        size=len(content),
        file_type=getattr(file, "content_type", "application/octet-stream"),
        url=f"/api/files/{stored_name}",
        file_path=str(target_path),
    )
    db.add(uploaded)
    await db.commit()

    return {
        "success": True,
        "file": {
            "id": file_id,
            "name": stored_name,
            "originalName": getattr(file, "filename", safe_name),
            "size": len(content),
            "type": getattr(file, "content_type", "application/octet-stream"),
            "url": f"/api/files/{stored_name}",
        }
    }


@router.get("/files", dependencies=[Depends(require_auth)])
async def list_files(db: AsyncSession = Depends(get_db)):
    """
    Lists uploaded files from database.
    """
    res = await db.execute(select(UploadedFile))
    files = res.scalars().all()
    return {
        "files": [
            {
                "id": f.id,
                "name": f.name,
                "originalName": f.original_name,
                "size": f.size,
                "type": f.file_type,
                "url": f.url,
                "uploadedAt": f.uploaded_at.isoformat() if f.uploaded_at else None,
            }
            for f in files
        ]
    }


@router.get("/files/{filename}", dependencies=[Depends(require_auth)])
async def get_uploaded_file(filename: str):
    """
    Serves an uploaded file with path traversal check.
    """
    safe_name = sanitize_filename(filename)
    target = verify_path_safe(settings.UPLOADS_DIR / safe_name, settings.UPLOADS_DIR)

    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Archivo no encontrado.")

    return FileResponse(target)


@router.get("/download-file", dependencies=[Depends(require_auth)])
async def download_created_file(filename: str):
    """
    Downloads a generated file from archivos_creados/ safely.
    """
    safe_name = sanitize_filename(filename)
    target = verify_path_safe(settings.ARCHIVOS_CREADOS_DIR / safe_name, settings.ARCHIVOS_CREADOS_DIR)

    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Archivo generado no encontrado.")

    return FileResponse(target, filename=safe_name)


@router.post("/save-generated-file", dependencies=[Depends(require_auth)])
async def save_generated_file(req: SaveFileRequest):
    """
    Saves an AI-generated file into archivos_creados/ with traversal check.
    """
    safe_name = sanitize_filename(req.filename)
    target = verify_path_safe(settings.ARCHIVOS_CREADOS_DIR / safe_name, settings.ARCHIVOS_CREADOS_DIR)

    with open(target, "w", encoding="utf-8") as f:
        f.write(req.content)

    return {
        "success": True,
        "filename": safe_name,
        "path": f"/api/download-file?filename={safe_name}",
        "message": f"Archivo '{safe_name}' guardado correctamente."
    }

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
from app.core.auth import (
    extract_token_from_request,
    is_owner_or_creator_authenticated,
    require_auth,
    verify_session_token,
)
from app.core.database import get_db
from app.core.models import UploadedFile

router = APIRouter(prefix="/api", tags=["files"])


def _get_tenant_owner_prefix(request: Request) -> Optional[str]:
    """
    Returns None if caller is host owner / CREATOR (full access),
    or returns '{uid}__' for standard SaaS tenants to isolate their files.
    """
    if is_owner_or_creator_authenticated(request):
        return None
    token = extract_token_from_request(request)
    if token:
        payload = verify_session_token(token)
        if payload and payload.get("type") == "saas_user" and payload.get("uid"):
            return f"{payload['uid']}__"
    return "anon__"

MAX_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB maximum upload size (DoS protection)
BLOCKED_UPLOAD_EXTENSIONS = {".exe", ".bat", ".cmd", ".vbs", ".scr", ".pif", ".msi"}


def sanitize_filename(filename: str) -> str:
    """Removes path traversal components and unsafe characters."""
    filename = Path(filename).name
    # Keep alphanumeric, dots, underscores, dashes
    filename = re.sub(r"[^\w\.-]", "_", filename)
    return filename or "unnamed_file"


def validate_upload_constraints(filename: str, content_len: int) -> None:
    """Enforces maximum upload size and blocks dangerous executable extensions."""
    http_413 = getattr(status, "HTTP_413_CONTENT_TOO_LARGE", 413)
    if content_len > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=http_413,
            detail=f"El archivo excede el tamaño máximo permitido ({MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB)."
        )
    ext = Path(filename).suffix.lower()
    if ext in BLOCKED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extensión de archivo ejecutable no permitida por seguridad ({ext})."
        )


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
        if len(b64_data) > int(MAX_UPLOAD_SIZE_BYTES * 1.4):
            raise HTTPException(
                status_code=getattr(status, "HTTP_413_CONTENT_TOO_LARGE", 413),
                detail="El archivo codificado en Base64 excede el límite de 25 MB."
            )
        try:
            content = base64.b64decode(b64_data)
        except Exception:
            raise HTTPException(status_code=400, detail="Formato base64 inválido")

        safe_name = sanitize_filename(raw_name)
        validate_upload_constraints(safe_name, len(content))
        tenant_prefix = _get_tenant_owner_prefix(request) or ""
        raw_uuid = str(uuid.uuid4())
        file_id = f"{tenant_prefix}{raw_uuid}"
        stored_name = f"{tenant_prefix}{raw_uuid[:8]}_{safe_name}"
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
    tenant_prefix = _get_tenant_owner_prefix(request) or ""
    raw_uuid = str(uuid.uuid4())
    file_id = f"{tenant_prefix}{raw_uuid}"
    stored_name = f"{tenant_prefix}{raw_uuid[:8]}_{safe_name}"
    target_path = settings.UPLOADS_DIR / stored_name
    verify_path_safe(target_path, settings.UPLOADS_DIR)

    content = await file.read(MAX_UPLOAD_SIZE_BYTES + 1)
    validate_upload_constraints(safe_name, len(content))
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
async def list_files(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Lists uploaded files from database, isolated per SaaS tenant (CREATOR sees all).
    """
    tenant_prefix = _get_tenant_owner_prefix(request)
    res = await db.execute(select(UploadedFile))
    files = res.scalars().all()
    if tenant_prefix is not None:
        files = [f for f in files if f.id.startswith(tenant_prefix) or f.name.startswith(tenant_prefix)]
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


@router.get("/files/catalog")
async def get_files_catalog(request: Request):
    """
    Lists catalog of generated and uploaded files for the Dynamic Viewer, isolated per tenant.
    """
    tenant_prefix = _get_tenant_owner_prefix(request)
    items = []
    # 1. Archivos creados (host owner / CREATOR only, or tenant-prefixed)
    if settings.ARCHIVOS_CREADOS_DIR.exists():
        for p in settings.ARCHIVOS_CREADOS_DIR.iterdir():
            if p.is_file():
                if tenant_prefix is not None and not p.name.startswith(tenant_prefix):
                    continue
                try:
                    st = p.stat()
                    items.append({
                        "name": p.name,
                        "folder": "archivos_creados",
                        "path": str(p),
                        "url": f"/api/download-file?filename={p.name}",
                        "size": st.st_size,
                        "extension": p.suffix.lower(),
                        "modified": st.st_mtime,
                    })
                except Exception:
                    continue

    # 2. Uploads
    if settings.UPLOADS_DIR.exists():
        for p in settings.UPLOADS_DIR.iterdir():
            if p.is_file():
                if tenant_prefix is not None and not p.name.startswith(tenant_prefix):
                    continue
                try:
                    st = p.stat()
                    items.append({
                        "name": p.name,
                        "folder": "uploads",
                        "path": str(p),
                        "url": f"/api/files/{p.name}",
                        "size": st.st_size,
                        "extension": p.suffix.lower(),
                        "modified": st.st_mtime,
                    })
                except Exception:
                    continue

    items.sort(key=lambda x: x["modified"], reverse=True)
    return {"ok": True, "files": items}


@router.get("/files/{filename}", dependencies=[Depends(require_auth)])
async def get_uploaded_file(filename: str, request: Request):
    """
    Serves an uploaded file with path traversal check and tenant ownership verification.
    """
    safe_name = sanitize_filename(filename)
    tenant_prefix = _get_tenant_owner_prefix(request)
    if tenant_prefix is not None and not safe_name.startswith(tenant_prefix):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: No tienes permiso para acceder a archivos de otro usuario.",
        )
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



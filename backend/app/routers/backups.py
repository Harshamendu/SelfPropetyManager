import os
import subprocess
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.config import settings
from app.dependencies import require_admin

router = APIRouter(tags=["Backups"], dependencies=[Depends(require_admin)])

BACKUP_DIR = os.path.join(settings.document_storage_path, "backups")
MAX_BACKUPS = 5


def _ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def _parse_db_url():
    """Extract host, port, user, password, dbname from sync_database_url."""
    url = settings.sync_database_url
    # postgresql://user:pass@host:port/dbname
    after_scheme = url.split("://", 1)[1]
    userpass, hostrest = after_scheme.split("@", 1)
    user, password = userpass.split(":", 1)
    hostport, dbname = hostrest.split("/", 1)
    if ":" in hostport:
        host, port = hostport.split(":", 1)
    else:
        host, port = hostport, "5432"
    return host, port, user, password, dbname


def _cleanup_old_backups():
    """Keep only the latest MAX_BACKUPS files."""
    _ensure_backup_dir()
    files = sorted(
        [
            f
            for f in os.listdir(BACKUP_DIR)
            if f.endswith(".sql")
        ],
        reverse=True,
    )
    for old_file in files[MAX_BACKUPS:]:
        os.remove(os.path.join(BACKUP_DIR, old_file))


class BackupInfo(BaseModel):
    filename: str
    size_bytes: int
    created_at: str


@router.get("/backups", response_model=list[BackupInfo])
async def list_backups():
    _ensure_backup_dir()
    files = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.endswith(".sql")],
        reverse=True,
    )
    result = []
    for f in files:
        path = os.path.join(BACKUP_DIR, f)
        stat = os.stat(path)
        result.append(
            BackupInfo(
                filename=f,
                size_bytes=stat.st_size,
                created_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            )
        )
    return result


@router.post("/backups", response_model=BackupInfo, status_code=status.HTTP_201_CREATED)
async def create_backup():
    _ensure_backup_dir()
    host, port, user, password, dbname = _parse_db_url()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"propmanager_{timestamp}.sql"
    filepath = os.path.join(BACKUP_DIR, filename)

    env = os.environ.copy()
    env["PGPASSWORD"] = password

    result = subprocess.run(
        [
            "pg_dump",
            "-h", host,
            "-p", port,
            "-U", user,
            "-d", dbname,
            "-f", filepath,
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"Backup failed: {result.stderr}",
        )

    _cleanup_old_backups()

    stat = os.stat(filepath)
    return BackupInfo(
        filename=filename,
        size_bytes=stat.st_size,
        created_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
    )


@router.get("/backups/{filename}/download")
async def download_backup(filename: str):
    filepath = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Backup not found")

    def iterfile():
        with open(filepath, "rb") as f:
            while chunk := f.read(1024 * 64):
                yield chunk

    return StreamingResponse(
        iterfile(),
        media_type="application/sql",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )


@router.post("/backups/restore/{filename}")
async def restore_backup(filename: str):
    filepath = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Backup not found")

    host, port, user, password, dbname = _parse_db_url()
    env = os.environ.copy()
    env["PGPASSWORD"] = password

    # Drop all connections and recreate
    drop_result = subprocess.run(
        [
            "psql",
            "-h", host,
            "-p", port,
            "-U", user,
            "-d", "postgres",
            "-c", f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{dbname}' AND pid <> pg_backend_pid();",
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )

    subprocess.run(
        [
            "psql",
            "-h", host,
            "-p", port,
            "-U", user,
            "-d", "postgres",
            "-c", f"DROP DATABASE IF EXISTS {dbname};",
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )

    subprocess.run(
        [
            "psql",
            "-h", host,
            "-p", port,
            "-U", user,
            "-d", "postgres",
            "-c", f"CREATE DATABASE {dbname};",
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Restore from backup
    restore_result = subprocess.run(
        [
            "psql",
            "-h", host,
            "-p", port,
            "-U", user,
            "-d", dbname,
            "-f", filepath,
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if restore_result.returncode != 0 and "ERROR" in restore_result.stderr:
        raise HTTPException(
            status_code=500,
            detail=f"Restore failed: {restore_result.stderr}",
        )

    return {"message": f"Database restored from {filename}"}


@router.delete(
    "/backups/{filename}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_backup(filename: str):
    filepath = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Backup not found")
    os.remove(filepath)


@router.post("/backups/upload", response_model=BackupInfo, status_code=status.HTTP_201_CREATED)
async def upload_backup(file: UploadFile):
    _ensure_backup_dir()

    if not file.filename or not file.filename.endswith(".sql"):
        raise HTTPException(
            status_code=400,
            detail="Only .sql backup files are accepted",
        )

    filepath = os.path.join(BACKUP_DIR, file.filename)
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    _cleanup_old_backups()

    stat = os.stat(filepath)
    return BackupInfo(
        filename=file.filename,
        size_bytes=stat.st_size,
        created_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
    )

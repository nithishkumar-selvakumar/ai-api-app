from pathlib import Path

from fastapi import HTTPException, UploadFile


UPLOAD_ROOT = Path("uploaded-docs")

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".csv",
    ".xlsx",
    ".xls",
    ".json",
}


def validate_project_name(project_name: str) -> str:
    """Return a safe project name that can be used as a directory name."""
    project_name = project_name.strip()

    if not project_name:
        raise HTTPException(
            status_code=400,
            detail="Project name is required",
        )

    if "/" in project_name or "\\" in project_name or ".." in project_name:
        raise HTTPException(
            status_code=400,
            detail="Invalid project name",
        )

    return project_name


def get_project_files(project_name: str) -> list[dict[str, int | str]]:
    """List the files already uploaded for a project."""
    project_name = validate_project_name(project_name)
    project_dir = UPLOAD_ROOT / project_name

    if not project_dir.is_dir():
        raise HTTPException(
            status_code=404,
            detail=f"Project not found: {project_name}",
        )

    return [
        {
            "filename": file_path.name,
            "path": str(file_path),
            "size": file_path.stat().st_size,
        }
        for file_path in sorted(project_dir.iterdir())
        if file_path.is_file()
    ]


def get_project_file(project_name: str, filename: str) -> Path:
    """Find a file in a project without permitting path traversal."""
    project_name = validate_project_name(project_name)
    safe_filename = Path(filename).name

    if not filename or safe_filename != filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = UPLOAD_ROOT / project_name / safe_filename

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {safe_filename}")

    return file_path


async def save_files(
    project_name: str,
    files: list[UploadFile],
):
    project_name = validate_project_name(project_name)

    if not files:
        raise HTTPException(
            status_code=400,
            detail="No files uploaded",
        )

    project_dir = UPLOAD_ROOT / project_name
    project_dir.mkdir(parents=True, exist_ok=True)

    uploaded_files = []

    for file in files:

        if not file.filename:
            continue

        # Get extension
        extension = Path(file.filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.filename}",
            )

        # Remove any directory components from filename
        filename = Path(file.filename).name

        file_path = project_dir / filename

        # Save file in chunks
        try:
            with file_path.open("wb") as buffer:
                while chunk := await file.read(1024 * 1024):
                    buffer.write(chunk)

        finally:
            await file.close()

        uploaded_files.append(
            {
                "filename": filename,
                "path": str(file_path),
                "size": file_path.stat().st_size,
            }
        )

    if not uploaded_files:
        raise HTTPException(
            status_code=400,
            detail="No valid files uploaded",
        )

    return {
        "message": "Files uploaded successfully",
        "project_name": project_name,
        "files": uploaded_files,
    }

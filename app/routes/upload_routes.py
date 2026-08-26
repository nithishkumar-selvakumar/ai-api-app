from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse

from app.controllers.upload_controller import (
    retrieve_project_file,
    retrieve_project_files,
    upload_files,
)


router = APIRouter(
    prefix="/api/files",
    tags=["Files"],
)


@router.post("/upload")
async def upload(
    project_name: str = Form(...),
    files: list[UploadFile] = File(...),
):
    return await upload_files(
        project_name=project_name,
        files=files,
    )


@router.get("/upload/{project_name}")
async def get_files_by_project(project_name: str):
    """Get metadata and download URLs for every file in a project."""
    files = retrieve_project_files(project_name)

    return {
        "project_name": project_name,
        "files": [
            {
                **file,
                "download_url": f"/api/files/upload/{project_name}/{file['filename']}",
            }
            for file in files
        ],
    }


@router.get("/upload/{project_name}/{filename}")
async def download_project_file(project_name: str, filename: str):
    """Download one uploaded file from a project."""
    file_path = retrieve_project_file(project_name, filename)
    return FileResponse(file_path, filename=file_path.name)

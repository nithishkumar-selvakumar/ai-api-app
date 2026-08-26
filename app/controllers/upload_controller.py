from fastapi import UploadFile

from app.services.upload_service import get_project_file, get_project_files, save_files


async def upload_files(
    project_name: str,
    files: list[UploadFile],
):
    return await save_files(
        project_name=project_name,
        files=files,
    )


def retrieve_project_files(project_name: str):
    return get_project_files(project_name)


def retrieve_project_file(project_name: str, filename: str):
    return get_project_file(project_name, filename)

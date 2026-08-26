from pydantic import BaseModel


class UploadedFile(BaseModel):
    filename: str
    path: str
    size: int


class UploadResponse(BaseModel):
    message: str
    project_name: str
    files: list[UploadedFile]
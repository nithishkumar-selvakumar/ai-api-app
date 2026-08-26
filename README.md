- uv run python -m uvicorn main:app --reload
- uv add -r requirements.txt
- ollama list

## Files API

- `POST /api/files/upload` uploads multipart files with a `project_name` field.
- `GET /api/files/upload/{project_name}` lists the files uploaded for a project.
- `GET /api/files/upload/{project_name}/{filename}` downloads one file.

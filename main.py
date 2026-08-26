from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.routes.upload_routes import router as upload_router


app = FastAPI(
    title="AI Defect Analyzer API",
    version="1.0.0",
)


app.include_router(upload_router)


def custom_openapi():
    """Use Swagger UI's binary-file schema for the multi-file upload field."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    upload_schema = openapi_schema["components"]["schemas"].get(
        "Body_upload_api_files_upload_post"
    )
    if upload_schema:
        upload_schema["properties"]["files"]["items"] = {
            "type": "string",
            "format": "binary",
        }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/health")
async def health():
    return {
        "status": "UP"
    }

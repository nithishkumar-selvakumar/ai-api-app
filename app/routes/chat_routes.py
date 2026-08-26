from fastapi import APIRouter

from app.controllers.chat_controller import ask
from app.models.chat_model import ChatRequest


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


@router.post("/{project_name}")
async def chat(
    project_name: str,
    request: ChatRequest,
):
    return ask(
        project_name=project_name,
        question=request.question,
        top_k=request.top_k,
    )
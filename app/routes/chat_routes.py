from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.controllers.chat_controller import ask
from app.database.connection import get_db
from app.models.chat_model import ChatRequest


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


@router.post("/{project_name}/ask")
async def chat(
    project_name: str,
    request: ChatRequest,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    print("Chat request received:", request)
    return ask(
        db=db,
        project_name=project_name,
        question=request.question,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        conversation_id=request.conversation_id,
    )
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.controllers.conversation_controller import (
    delete_conversation,
    get_conversation,
    get_project_conversations,
)
from app.database.connection import get_db


router = APIRouter(
    prefix="/api/conversations",
    tags=["Conversations"],
)


@router.get("/{project_name}")
async def conversations(
    project_name: str,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    return get_project_conversations(
        db=db,
        project_name=project_name,
    )


@router.get("/detail/{conversation_id}")
async def conversation(
    conversation_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    return get_conversation(
        db=db,
        conversation_id=conversation_id,
    )


@router.delete("/{conversation_id}")
async def delete(
    conversation_id: int,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    return delete_conversation(
        db=db,
        conversation_id=conversation_id,
    )
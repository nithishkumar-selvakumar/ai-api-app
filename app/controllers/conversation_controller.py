from sqlalchemy.orm import Session

from app.services.conversation_service import (
    get_conversation_detail,
    list_conversations,
    remove_conversation,
)


def get_project_conversations(
    db: Session,
    project_name: str,
):
    return list_conversations(
        db,
        project_name,
    )


def get_conversation(
    db: Session,
    conversation_id: int,
):
    return get_conversation_detail(
        db,
        conversation_id,
    )


def delete_conversation(
    db: Session,
    conversation_id: int,
):
    return remove_conversation(
        db,
        conversation_id,
    )
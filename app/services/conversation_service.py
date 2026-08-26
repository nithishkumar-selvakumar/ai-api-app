from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.chat_repository import (
    delete_conversation,
    get_conversation,
    get_messages,
    get_project_conversations,
)


def list_conversations(
    db: Session,
    project_name: str,
):
    conversations = get_project_conversations(
        db,
        project_name,
    )

    return [
        {
            "id": conversation.id,
            "project_name": conversation.project_name,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
        }
        for conversation in conversations
    ]


def get_conversation_detail(
    db: Session,
    conversation_id: int,
):
    conversation = get_conversation(
        db,
        conversation_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    messages = get_messages(
        db,
        conversation_id,
    )

    return {
        "id": conversation.id,
        "project_name": conversation.project_name,
        "title": conversation.title,
        "messages": [
            {
                "id": message.id,
                "conversation_id": message.conversation_id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            }
            for message in messages
        ],
    }


def remove_conversation(
    db: Session,
    conversation_id: int,
):
    deleted = delete_conversation(
        db,
        conversation_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return {
        "message": "Conversation deleted successfully",
        "conversation_id": conversation_id,
    }
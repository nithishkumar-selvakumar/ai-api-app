from sqlalchemy.orm import Session

from app.models.chat_entity import (
    Conversation,
    Message,
)


def create_conversation(
    db: Session,
    project_name: str,
    title: str | None = None,
):
    conversation = Conversation(
        project_name=project_name,
        title=title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def add_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
):
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_conversation(
    db: Session,
    conversation_id: int,
):
    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id
        )
        .first()
    )


def get_messages(
    db: Session,
    conversation_id: int,
):
    return (
        db.query(Message)
        .filter(
            Message.conversation_id
            == conversation_id
        )
        .order_by(Message.created_at)
        .all()
    )


def get_project_conversations(
    db: Session,
    project_name: str,
):
    return (
        db.query(Conversation)
        .filter(
            Conversation.project_name
            == project_name
        )
        .order_by(
            Conversation.updated_at.desc()
        )
        .all()
    )


def delete_conversation(
    db: Session,
    conversation_id: int,
):
    conversation = get_conversation(
        db,
        conversation_id,
    )

    if not conversation:
        return False

    db.delete(conversation)
    db.commit()

    return True
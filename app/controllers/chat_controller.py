from sqlalchemy.orm import Session

from app.services.chat_service import ask_project


def ask(
    db: Session,
    project_name: str,
    question: str,
    top_k: int,
    conversation_id: int | None,
):
    return ask_project(
        db=db,
        project_name=project_name,
        question=question,
        top_k=top_k,
        conversation_id=conversation_id,
    )
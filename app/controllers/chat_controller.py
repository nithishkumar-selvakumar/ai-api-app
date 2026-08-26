from sqlalchemy.orm import Session

from app.services.chat_service import ask_project


def ask(
    db: Session,
    project_name: str,
    question: str,
    top_k: int,
    score_threshold: float,
    conversation_id: int | None,
):

    return ask_project(
        db=db,
        project_name=project_name,
        question=question,
        top_k=top_k,
        score_threshold=score_threshold,
        conversation_id=conversation_id,
    )
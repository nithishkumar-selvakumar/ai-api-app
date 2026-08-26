from sqlalchemy.orm import Session

from app.repositories.chat_repository import (
    add_message,
    create_conversation,
    get_conversation,
    get_messages,
)
from app.utils.llm import generate_answer
from app.utils.vector_search import search_vectors


def ask_project(
    db: Session,
    project_name: str,
    question: str,
    top_k: int = 5,
    score_threshold: float = 0.3,
    conversation_id: int | None = None,
):

    # -----------------------------
    # Conversation
    # -----------------------------

    if conversation_id:

        conversation = get_conversation(
            db,
            conversation_id,
        )

        if not conversation:
            raise ValueError(
                "Conversation not found"
            )

        if conversation.project_name != project_name:
            raise ValueError(
                "Conversation does not belong "
                "to this project"
            )

    else:

        conversation = create_conversation(
            db=db,
            project_name=project_name,
            title=question[:100],
        )

    # -----------------------------
    # Previous messages
    # -----------------------------

    messages = get_messages(
        db,
        conversation.id,
    )

    history = "\n".join(
        [
            f"{message.role}: {message.content}"
            for message in messages[-10:]
        ]
    )

    # -----------------------------
    # Vector search
    # -----------------------------

    search_results = search_vectors(
        project_name=project_name,
        query=question,
        top_k=top_k,
        score_threshold=score_threshold,
    )

    # -----------------------------
    # No relevant documents
    # -----------------------------

    if not search_results:

        answer = (
            "The information is not available "
            "in the uploaded documents."
        )

        add_message(
            db,
            conversation.id,
            "user",
            question,
        )

        add_message(
            db,
            conversation.id,
            "assistant",
            answer,
        )

        return {
            "conversation_id": conversation.id,
            "question": question,
            "answer": answer,
            "sources": [],
        }

    # -----------------------------
    # Context
    # -----------------------------

    context_parts = []

    sources = []

    for document, score in search_results:

        context_parts.append(
            document.page_content
        )

        sources.append(
            {
                "filename": document.metadata.get(
                    "filename",
                    "unknown",
                ),
                "page": document.metadata.get(
                    "page",
                    None,
                ),
                "chunk_index": document.metadata.get(
                    "chunk_index",
                    -1,
                ),
                "score": round(score, 4),
            }
        )

    context = "\n\n".join(
        context_parts
    )

    # -----------------------------
    # LLM
    # -----------------------------

    answer = generate_answer(
        question=question,
        context=context,
        history=history,
    )

    # -----------------------------
    # Save user message
    # -----------------------------

    add_message(
        db,
        conversation.id,
        "user",
        question,
    )

    # -----------------------------
    # Save assistant message
    # -----------------------------

    add_message(
        db,
        conversation.id,
        "assistant",
        answer,
    )

    # -----------------------------
    # Response
    # -----------------------------

    return {
        "conversation_id": conversation.id,
        "question": question,
        "answer": answer,
        "sources": sources,
    }
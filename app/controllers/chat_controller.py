from app.services.chat_service import ask_project


def ask(
    project_name: str,
    question: str,
    top_k: int = 5,
):
    return ask_project(
        project_name=project_name,
        question=question,
        top_k=top_k,
    )
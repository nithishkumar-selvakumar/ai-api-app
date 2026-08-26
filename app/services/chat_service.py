from app.utils.llm import generate_answer
from app.utils.vector_search import search_vectors


def ask_project(
    project_name: str,
    question: str,
    top_k: int = 5,
):

    documents = search_vectors(
        project_name=project_name,
        query=question,
        top_k=top_k,
    )

    if not documents:
        return {
            "question": question,
            "answer": (
                "No relevant information was "
                "found in the uploaded documents."
            ),
            "sources": [],
        }

    context_parts = []

    sources = []

    for document in documents:

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
            }
        )

    context = "\n\n".join(
        context_parts
    )

    answer = generate_answer(
        question=question,
        context=context,
    )

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
    }
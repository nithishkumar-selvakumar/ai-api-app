from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings


OLLAMA_BASE_URL = "http://localhost:11434"

EMBEDDING_MODEL = "nomic-embed-text"

CHROMA_PATH = "chroma-data"


_embeddings = OllamaEmbeddings(
    model=EMBEDDING_MODEL,
    base_url=OLLAMA_BASE_URL,
)


def create_vector_store(
    project_name: str,
    chunks: list[Document],
) -> int:

    if not chunks:
        return 0

    collection_name = f"project_{project_name}"

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=_embeddings,
        persist_directory=CHROMA_PATH,
    )

    ids = []

    for index, chunk in enumerate(chunks):

        filename = chunk.metadata.get(
            "filename",
            "unknown",
        )

        chunk_id = (
            f"{project_name}:"
            f"{filename}:"
            f"{index}"
        )

        ids.append(chunk_id)

    vector_store.add_documents(
        documents=chunks,
        ids=ids,
    )

    return len(chunks)
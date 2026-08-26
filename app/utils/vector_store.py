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


def get_collection_name(project_name: str) -> str:
    return f"project_{project_name}"


def get_vector_store(project_name: str) -> Chroma:
    return Chroma(
        collection_name=get_collection_name(project_name),
        embedding_function=_embeddings,
        persist_directory=CHROMA_PATH,
    )


def create_vector_store(
    project_name: str,
    chunks: list[Document],
) -> int:

    if not chunks:
        return 0

    vector_store = get_vector_store(
        project_name
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

    print(
        f"Added {len(chunks)} vectors "
        f"to {get_collection_name(project_name)}"
    )

    return len(chunks)
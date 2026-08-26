from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings


OLLAMA_BASE_URL = "http://localhost:11434"

EMBEDDING_MODEL = "nomic-embed-text"

CHROMA_PATH = "chroma-data"


_embeddings = OllamaEmbeddings(
    model=EMBEDDING_MODEL,
    base_url=OLLAMA_BASE_URL,
)


def get_vector_store(
    project_name: str,
) -> Chroma:

    collection_name = f"project_{project_name}"

    return Chroma(
        collection_name=collection_name,
        embedding_function=_embeddings,
        persist_directory=CHROMA_PATH,
    )


def search_vectors(
    project_name: str,
    query: str,
    top_k: int = 5,
):
    vector_store = get_vector_store(
        project_name
    )

    results = vector_store.similarity_search(
        query,
        k=top_k,
    )

    return results
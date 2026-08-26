from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)


def create_chunks(
    documents: list[Document],
) -> list[Document]:

    valid_documents = [
        document
        for document in documents
        if document.page_content
        and document.page_content.strip()
    ]

    print(
        f"Documents received: {len(documents)}"
    )

    print(
        f"Documents with text: {len(valid_documents)}"
    )

    for index, document in enumerate(valid_documents):
        print(
            f"Document {index + 1}: "
            f"{len(document.page_content)} characters"
        )

    chunks = _splitter.split_documents(
        valid_documents
    )

    print(
        f"Chunks created: {len(chunks)}"
    )

    return chunks
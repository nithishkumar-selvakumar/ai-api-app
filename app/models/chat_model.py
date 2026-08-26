from pydantic import BaseModel


class ChatRequest(BaseModel):

    question: str

    top_k: int = 5

    conversation_id: int | None = None


class Source(BaseModel):

    filename: str

    page: int | None = None

    chunk_index: int


class ChatResponse(BaseModel):

    conversation_id: int

    question: str

    answer: str

    sources: list[Source]
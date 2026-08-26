from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    top_k: int = 5


class Source(BaseModel):
    filename: str
    chunk_index: int


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: list[Source]
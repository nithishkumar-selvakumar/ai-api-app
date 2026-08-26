from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    top_k: int = 5
    score_threshold: float = 0.3
    conversation_id: int | None = None


class Source(BaseModel):
    filename: str
    page: int | None = None
    chunk_index: int
    score: float


class ChatResponse(BaseModel):
    conversation_id: int
    question: str
    answer: str
    sources: list[Source]


class ConversationResponse(BaseModel):
    id: int
    project_name: str
    title: str | None
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: str


class ConversationDetailResponse(BaseModel):
    id: int
    project_name: str
    title: str | None
    messages: list[MessageResponse]
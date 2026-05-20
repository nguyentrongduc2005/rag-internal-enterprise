from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str
    conversation_id: UUID | None = None
    document_id: str | None = None
    k: int = 5


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: list[dict]


class ConversationCreate(BaseModel):
    title: str | None = None


class ConversationResponse(BaseModel):
    id: UUID
    owner_id: str | None
    title: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    token_count: int | None
    created_at: datetime

    class Config:
        from_attributes = True

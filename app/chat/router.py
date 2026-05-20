import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.chat.schemas import (
    ChatMessageResponse,
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
)
from app.chat.service import ChatService
from app.database import get_db
from app.retrieval.llm import get_qwen_chat_model
from app.shared.security import get_current_user


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ChatService(db)
    try:
        return service.chat(
            question=payload.question,
            conversation_id=payload.conversation_id,
            document_id=payload.document_id,
            current_user=current_user,
            k=payload.k,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/stream")
def chat_stream(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ChatService(db)
    try:
        conversation, prompt, chunks = service.prepare_chat(
            question=payload.question,
            conversation_id=payload.conversation_id,
            document_id=payload.document_id,
            current_user=current_user,
            k=payload.k,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    def event_stream():
        sources = service.build_sources(chunks)
        yield _json_line(
            {
                "type": "meta",
                "conversation_id": str(conversation.id),
                "sources": sources,
            }
        )

        answer_parts: list[str] = []
        llm = get_qwen_chat_model(streaming=True)

        try:
            for chunk in llm.stream(prompt):
                token = chunk.content or ""
                if not token:
                    continue
                answer_parts.append(token)
                yield _json_line({"type": "token", "content": token})

            answer = "".join(answer_parts)
            service.add_message(conversation.id, "assistant", answer)
            yield _json_line({"type": "done", "answer": answer})
        except Exception as exc:
            yield _json_line({"type": "error", "detail": str(exc)})

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


def _json_line(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False) + "\n"


@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ChatService(db).create_conversation(owner_id=current_user.id, title=payload.title)


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return ChatService(db).list_conversations(current_user)


@router.get("/conversations/{conversation_id}/messages", response_model=list[ChatMessageResponse])
def list_messages(
    conversation_id: UUID,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ChatService(db)
    try:
        return service.get_messages(conversation_id, current_user=current_user, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

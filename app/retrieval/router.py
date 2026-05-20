from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.retrieval.service import RetrievalService
from app.retrieval.reranker import SimpleReranker
from app.retrieval.prompt_builder import PromptBuilder
from app.retrieval.llm import get_qwen_chat_model
from app.shared.security import get_current_user


router = APIRouter(prefix="/retrieval", tags=["retrieval"])


class AskRequest(BaseModel):
    question: str
    document_id: str | None = None
    k: int = 5


class AskResponse(BaseModel):
    answer: str
    sources: list[dict]


@router.post("/ask", response_model=AskResponse)
def ask(
    request: AskRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    retriever = RetrievalService(db)
    reranker = SimpleReranker()
    prompt_builder = PromptBuilder()

    chunks = retriever.search(
        question=request.question,
        k=request.k,
        user_id=current_user.id,
        include_all=current_user.role == "admin",
        document_id=request.document_id,
    )

    chunks = reranker.rerank(
        question=request.question,
        chunks=chunks,
    )

    prompt = prompt_builder.build(
        question=request.question,
        chunks=chunks,
    )

    llm = get_qwen_chat_model()

    answer = llm.invoke(prompt).content

    sources = [
        {
            "document_id": str(chunk["document_id"]),
            "filename": chunk["filename"],
            "page_number": chunk["page_number"],
            "chunk_index": chunk["chunk_index"],
            "score": float(chunk["score"]),
            "content_preview": chunk["content"][:300],
        }
        for chunk in chunks
    ]

    return AskResponse(
        answer=answer,
        sources=sources,
    )

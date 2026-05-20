from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.chat.models import Conversation, ChatMessage
from app.retrieval.llm import get_qwen_chat_model
from app.retrieval.service import RetrievalService
from app.retrieval.reranker import SimpleReranker
from app.retrieval.prompt_builder import PromptBuilder


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def create_conversation(self, owner_id: str, title: str | None = None):
        conversation = Conversation(owner_id=owner_id, title=title)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: UUID, current_user):
        conversation = self.db.get(Conversation, conversation_id)
        if conversation is None:
            return None
        if current_user.role != "admin" and conversation.owner_id != current_user.id:
            return None
        return conversation

    def list_conversations(self, current_user):
        stmt = select(Conversation).order_by(Conversation.updated_at.desc())
        if current_user.role != "admin":
            stmt = stmt.where(Conversation.owner_id == current_user.id)
        return self.db.execute(stmt).scalars().all()

    def get_messages(self, conversation_id: UUID, current_user=None, limit: int = 10):
        if current_user is not None and self.get_conversation(conversation_id, current_user) is None:
            raise ValueError("Conversation not found")

        stmt = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )

        messages = self.db.execute(stmt).scalars().all()
        return list(reversed(messages))

    def add_message(self, conversation_id: UUID, role: str, content: str):
        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def chat(
        self,
        question: str,
        current_user,
        conversation_id: UUID | None = None,
        document_id: str | None = None,
        k: int = 5,
    ):
        conversation, prompt, chunks = self.prepare_chat(
            question=question,
            current_user=current_user,
            conversation_id=conversation_id,
            document_id=document_id,
            k=k,
        )

        llm = get_qwen_chat_model()
        answer = llm.invoke(prompt).content

        self.add_message(conversation.id, "assistant", answer)

        return {
            "conversation_id": str(conversation.id),
            "answer": answer,
            "sources": self.build_sources(chunks),
        }

    def prepare_chat(
        self,
        question: str,
        current_user,
        conversation_id: UUID | None = None,
        document_id: str | None = None,
        k: int = 5,
    ):
        if conversation_id is None:
            conversation = self.create_conversation(owner_id=current_user.id, title=question[:80])
        else:
            conversation = self.get_conversation(conversation_id, current_user)
            if conversation is None:
                raise ValueError("Conversation not found")

        self.add_message(conversation.id, "user", question)

        history = self.get_messages(conversation.id, limit=8)

        retriever = RetrievalService(self.db)
        reranker = SimpleReranker()
        prompt_builder = PromptBuilder()

        chunks = retriever.search(
            question=question,
            k=k,
            user_id=current_user.id,
            include_all=current_user.role == "admin",
            document_id=document_id,
        )
        chunks = reranker.rerank(question=question, chunks=chunks)

        prompt = prompt_builder.build(
            question=self._build_standalone_question(question, history),
            chunks=chunks,
        )

        return conversation, prompt, chunks

    def build_sources(self, chunks: list[dict]) -> list[dict]:
        return [
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

    def _build_standalone_question(self, question: str, history: list[ChatMessage]) -> str:
        history_text = "\n".join(
            f"{msg.role}: {msg.content}"
            for msg in history[-6:]
        )

        return f"""
Conversation history:
{history_text}

Current question:
{question}
""".strip()

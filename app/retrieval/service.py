from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ingestion.embedding import get_embeddings


class RetrievalService:
    def __init__(self, db: Session):
        self.db = db
        self.embeddings = get_embeddings()

    def search(
        self,
        question: str,
        k: int = 5,
        user_id: str | None = None,
        include_all: bool = False,
        document_id: str | None = None,
    ):
        query_vector = self.embeddings.embed_query(question)
        filters = ["d.status = 'READY'"]
        params = {
            "query_vector": str(query_vector),
            "k": k,
        }
        if not include_all:
            filters.append("(d.owner_id = :user_id OR d.owner_id IS NULL)")
            params["user_id"] = user_id
        if document_id:
            filters.append("d.id = :document_id")
            params["document_id"] = document_id
        elif self._looks_like_cv_question(question):
            filters.append("d.file_name ILIKE :filename_hint")
            params["filename_hint"] = "%cv%"

        where_clause = " AND ".join(filters)

        sql = text(f"""
            SELECT
                dc.id,
                dc.document_id,
                dc.chunk_index,
                dc.content,
                dc.page_number,
                dc.source,
                d.file_name AS filename,
                1 - (dc.embedding <=> CAST(:query_vector AS vector)) AS score
            FROM document_chunks dc
            JOIN documents d ON d.id = dc.document_id
            WHERE {where_clause}
            ORDER BY dc.embedding <=> CAST(:query_vector AS vector)
            LIMIT :k
        """)

        result = self.db.execute(sql, params)

        return [dict(row._mapping) for row in result]

    def _looks_like_cv_question(self, question: str) -> bool:
        normalized = question.lower()
        return any(keyword in normalized for keyword in ["cv", "resume", "curriculum vitae", "sơ yếu", "lý lịch"])

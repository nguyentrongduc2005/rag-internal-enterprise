from sqlalchemy.orm import Session

from app.documents.models import DocumentChunk


class DocumentIndexer:
    def index(
        self,
        db: Session,
        document_id,
        chunks,
        embeddings: list[list[float]],
    ):
        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).delete()

        records = []

        for index, chunk in enumerate(chunks):
            metadata = chunk.metadata or {}
            
            # Remove NUL characters (\x00) from PostgreSQL Text fields
            clean_content = chunk.page_content.replace('\x00', '')
            
            records.append(
                DocumentChunk(
                    document_id=document_id,
                    chunk_index=index,
                    content=clean_content,
                    embedding=embeddings[index],
                    page_number=metadata.get("page"),
                    source=metadata.get("source"),
                )
            )

        db.add_all(records)
        db.commit()
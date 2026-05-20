import os
import tempfile

from app.celery_app import celery_app
from app.database import SessionLocal
from app import models
from app.documents.models import Document
from app.shared.storage import storage

from app.ingestion.parser import DocumentParser
from app.ingestion.chunker import DocumentChunker
from app.ingestion.embedding import embed_texts
from app.ingestion.indexer import DocumentIndexer


@celery_app.task(name="app.ingestion.tasks.ingest_document")
def ingest_document(document_id: str):
    db = SessionLocal()
    temp_path = None

    try:
        document = db.query(Document).filter(
            Document.id == document_id
        ).first()

        if document is None:
            raise ValueError("Document not found")

        document.status = "PROCESSING"
        document.error_message = None
        db.commit()

        suffix = os.path.splitext(document.file_name)[-1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_path = tmp.name

        storage.fget_object(
            bucket_name=document.bucket_name,
            object_name=document.object_key,
            file_path=temp_path,
        )

        parser = DocumentParser()
        chunker = DocumentChunker()
        indexer = DocumentIndexer()

        docs = parser.parse(temp_path)

        for doc in docs:
            doc.metadata["document_id"] = str(document.id)
            doc.metadata["filename"] = document.file_name
            doc.metadata["object_name"] = document.object_key

        chunks = chunker.split(docs)

        if not chunks:
            raise ValueError("No chunks generated from document")

        texts = [chunk.page_content for chunk in chunks]

        embeddings = embed_texts(texts)

        indexer.index(
            db=db,
            document_id=document.id,
            chunks=chunks,
            embeddings=embeddings,
        )

        document.status = "READY"
        document.chunk_count = len(chunks)
        document.error_message = None
        db.commit()

    except Exception as e:
        db.rollback()

        document = db.query(Document).filter(
            Document.id == document_id
        ).first()

        if document:
            document.status = "FAILED"
            document.error_message = str(e)
            db.commit()

        raise

    finally:
        db.close()

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

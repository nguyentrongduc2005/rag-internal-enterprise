from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.config import settings
from app.documents.models import Document
from app.shared.storage import storage


def create_document(db: Session, file: UploadFile) -> Document:
    object_key, size = storage.upload_file(file)

    document = Document(
        title=file.filename,
        file_name=file.filename,
        bucket_name=settings.MINIO_BUCKET,
        object_key=object_key,
        content_type=file.content_type,
        size_bytes=size,
        status="UPLOADED",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_documents(db: Session) -> list[Document]:
    return db.query(Document).order_by(Document.created_at.desc()).all()


def get_document_by_id(db: Session, document_id: str) -> Document | None:
    return db.query(Document).filter(Document.id == document_id).first()


def get_document_download_url(db: Session, document_id: str) -> str | None:
    document = get_document_by_id(db, document_id)

    if not document:
        return None

    return storage.get_presigned_url(document.object_key)


def delete_document(db: Session, document_id: str) -> bool:
    document = get_document_by_id(db, document_id)

    if not document:
        return False

    storage.delete_file(document.object_key)

    db.delete(document)
    db.commit()

    return True
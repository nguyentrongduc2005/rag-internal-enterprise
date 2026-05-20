from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.config import settings
from app.documents.models import Document
from app.ingestion.tasks import ingest_document
from app.shared.storage import storage


def create_document(db: Session, file: UploadFile, owner_id: str) -> Document:
    object_key, size = storage.upload_file(file)

    document = Document(
        title=file.filename,
        file_name=file.filename,
        owner_id=owner_id,
        bucket_name=settings.MINIO_BUCKET,
        object_key=object_key,
        content_type=file.content_type,
        size_bytes=size,
        status="UPLOADED",
    )

    db.add(document)
    db.commit()
    db.refresh(document)
    ingest_document.delay(str(document.id))

    return document


def get_documents(db: Session, current_user) -> list[Document]:
    query = db.query(Document)
    if current_user.role != "admin":
        query = query.filter((Document.owner_id == current_user.id) | (Document.owner_id.is_(None)))
    return query.order_by(Document.created_at.desc()).all()


def get_document_by_id(db: Session, document_id: str, current_user=None) -> Document | None:
    query = db.query(Document).filter(Document.id == document_id)
    if current_user is not None and current_user.role != "admin":
        query = query.filter((Document.owner_id == current_user.id) | (Document.owner_id.is_(None)))
    return query.first()


def get_document_download_url(db: Session, document_id: str, current_user) -> str | None:
    document = get_document_by_id(db, document_id, current_user)

    if not document:
        return None

    return storage.get_presigned_url(document.object_key)


def delete_document(db: Session, document_id: str, current_user) -> bool:
    document = get_document_by_id(db, document_id, current_user)

    if not document:
        return False

    storage.delete_file(document.object_key)

    db.delete(document)
    db.commit()

    return True

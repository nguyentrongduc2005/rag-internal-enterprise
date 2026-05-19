from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.documents import service
from app.documents.schemas import DocumentResponse, DocumentDownloadResponse


router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return service.create_document(db, file)


@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    return service.get_documents(db)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    document = service.get_document_by_id(db, document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.get("/{document_id}/download-url", response_model=DocumentDownloadResponse)
def get_download_url(
    document_id: str,
    db: Session = Depends(get_db)
):
    url = service.get_document_download_url(db, document_id)

    if not url:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"url": url}


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    deleted = service.delete_document(db, document_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"message": "Document deleted"}
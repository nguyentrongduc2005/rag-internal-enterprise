from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.documents import service
from app.documents.schemas import DocumentResponse, DocumentDownloadResponse
from app.shared.security import get_current_user


router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv"}

@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")
        
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type '{file_ext}'. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    return service.create_document(db, file, owner_id=current_user.id)


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return service.get_documents(db, current_user)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    document = service.get_document_by_id(db, document_id, current_user)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.get("/{document_id}/download-url", response_model=DocumentDownloadResponse)
def get_download_url(
    document_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    url = service.get_document_download_url(db, document_id, current_user)

    if not url:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"url": url}


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    deleted = service.delete_document(db, document_id, current_user)

    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"message": "Document deleted"}

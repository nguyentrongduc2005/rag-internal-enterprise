from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    title: str
    file_name: str
    bucket_name: str
    object_key: str
    content_type: str | None
    size_bytes: int | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentDownloadResponse(BaseModel):
    url: str
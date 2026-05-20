from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    title: str
    file_name: str
    owner_id: str | None = None
    bucket_name: str
    object_key: str
    content_type: str | None
    size_bytes: int | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# model_config = ConfigDict(from_attributes=True)
class DocumentDownloadResponse(BaseModel):
    url: str

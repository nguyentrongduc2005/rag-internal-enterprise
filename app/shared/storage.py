import uuid
from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
from app.config import settings


class MinioStorage:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self):
        exists = self.client.bucket_exists(self.bucket)
        if not exists:
            self.client.make_bucket(self.bucket)

    def upload_file(self, file: UploadFile) -> tuple[str, int]:
        object_key = f"documents/{uuid.uuid4()}-{file.filename}"

        file.file.seek(0, 2)  # Seek to the end to get file size
        size = file.file.tell()
        file.file.seek(0)  # Seek back to start for the actual upload

        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_key,
            data=file.file,
            length=size,
            content_type=file.content_type,
        )

        return object_key, size

    def download_file(self, object_key: str) -> bytes:
        response = self.client.get_object(
            bucket_name=self.bucket,
            object_name=object_key,
        )

        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def delete_file(self, object_key: str):
        self.client.remove_object(
            bucket_name=self.bucket,
            object_name=object_key,
        )

    def get_presigned_url(self, object_key: str) -> str:
        return self.client.presigned_get_object(
            bucket_name=self.bucket,
            object_name=object_key,
        )
    
    def fget_object(self, bucket_name: str, object_name: str, file_path: str):
        self.client.fget_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path,
        )


storage = MinioStorage()
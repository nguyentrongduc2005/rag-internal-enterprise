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

        file.file.seek(0)

        size = 0
        chunks = []

        while chunk := file.file.read(1024 * 1024):
            size += len(chunk)
            chunks.append(chunk)

        from io import BytesIO

        data = BytesIO(b"".join(chunks))

        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_key,
            data=data,
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


storage = MinioStorage()
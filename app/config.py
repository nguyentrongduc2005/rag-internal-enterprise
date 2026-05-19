from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str = "rag-documents"
    MINIO_SECURE: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
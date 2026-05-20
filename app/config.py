from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET: str = "rag-documents"
    MINIO_SECURE: bool = False

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    HUGGINGFACEHUB_API_TOKEN: str

    class Config:
        env_file = ".env"


settings = Settings()

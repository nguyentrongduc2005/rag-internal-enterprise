import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)

    bucket_name: Mapped[str] = mapped_column(String(255), nullable=False)

    object_key: Mapped[str] = mapped_column(Text, nullable=False)

    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    size_bytes: Mapped[int | None] = mapped_column(nullable=True)

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="UPLOADED"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, BigInteger, Text, DateTime, Enum
from sqlalchemy.dialects.mysql import CHAR
from config.database import Base

class CvDocument(Base):
    __tablename__ = "cv_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(CHAR(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    file_name = Column(String(255), nullable=False)
    original_file_name = Column(String(255), nullable=False)
    file_extension = Column(String(10), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    storage_path = Column(String(500), nullable=False)
    total_pages = Column(Integer, nullable=True)
    upload_source = Column(String(100), nullable=True)
    uploaded_by = Column(String(100), nullable=True)

    status = Column(
        Enum(
            "uploaded", "queued_for_ocr", "processing_ocr",
            "ocr_completed", "ocr_failed", "queued_for_parsing",
            "parsing_completed", "parsing_failed", "analyzed", "archived"
        ),
        nullable=False,
        default="uploaded"
    )
    error_message = Column(Text, nullable=True)

    uploaded_at = Column(DateTime, nullable=True)
    ocr_started_at = Column(DateTime, nullable=True)
    ocr_completed_at = Column(DateTime, nullable=True)
    parsing_started_at = Column(DateTime, nullable=True)
    parsing_completed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
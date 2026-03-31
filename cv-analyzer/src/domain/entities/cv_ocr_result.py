from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Float, ForeignKey, Enum
from config.database import Base

class CvOcrResult(Base):
    __tablename__ = "cv_ocr_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cv_document_id = Column(Integer, ForeignKey("cv_documents.id"), nullable=False)
    page_number = Column(Integer, nullable=False, default=1)
    raw_text = Column(Text, nullable=True)
    raw_json_result = Column(Text, nullable=True)
    confidence_average = Column(Float, nullable=True)
    processing_duration_ms = Column(Integer, nullable=True)
    status = Column(
        Enum("pending", "completed", "failed"),
        nullable=False,
        default="pending"
    )
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
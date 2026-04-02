"""
ORM Model: candidate_profiles
Layer   : Infrastructure > Persistence > Models
Fungsi  : Mapping tabel candidate_profiles ke SQLAlchemy ORM
Phase   : 2 - Basic Parser
"""

from sqlalchemy import (
    Column, Integer, String, Text,
    DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from config.database import Base


class CandidateProfileModel(Base):
    """
    Representasi tabel candidate_profiles di database.
    Menyimpan hasil parsing kandidat sebagai entitas utama.
    """

    __tablename__ = "candidate_profiles"

    # ── Primary Key ────────────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), nullable=False, unique=True)

    # ── Foreign Key ────────────────────────────────────────────────────────────
    cv_document_id = Column(
        Integer,
        ForeignKey("cv_documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True  # 1 dokumen hanya punya 1 candidate profile
    )

    # ── Identitas Kandidat ─────────────────────────────────────────────────────
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    alternate_phone_number = Column(String(50), nullable=True)
    current_location = Column(String(255), nullable=True)
    address_text = Column(Text, nullable=True)

    # ── Informasi Profesional ──────────────────────────────────────────────────
    professional_summary = Column(Text, nullable=True)
    date_of_birth_text = Column(String(100), nullable=True)
    total_experience_text = Column(String(255), nullable=True)
    estimated_total_experience_months = Column(Integer, nullable=True)
    latest_job_title = Column(String(255), nullable=True)
    latest_company_name = Column(String(255), nullable=True)

    # ── Social Links ───────────────────────────────────────────────────────────
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)

    # ── Parser Metadata ────────────────────────────────────────────────────────
    raw_text = Column(Text, nullable=True)          # full raw OCR text yg diparse
    parser_version = Column(String(50), nullable=True, default="1.0.0")
    parser_status = Column(String(50), nullable=True, default="pending")
    parser_notes = Column(Text, nullable=True)

    # ── Timestamps ─────────────────────────────────────────────────────────────
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    deleted_at = Column(DateTime, nullable=True)

    # ── Relationships ──────────────────────────────────────────────────────────
    skills = relationship(
        "CandidateSkillModel",
        back_populates="candidate_profile",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<CandidateProfileModel "
            f"id={self.id} "
            f"name='{self.full_name}' "
            f"status='{self.parser_status}'>"
        )
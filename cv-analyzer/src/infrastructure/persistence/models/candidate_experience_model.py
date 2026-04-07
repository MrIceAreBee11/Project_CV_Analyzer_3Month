"""
ORM Model: candidate_experiences
Layer   : Infrastructure > Persistence > Models
Fungsi  : Mapping tabel candidate_experiences ke SQLAlchemy ORM
Phase   : 3 - Structured Candidate Data
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from config.database import Base

class CandidateExperienceModel(Base):
    """
    Representasi tabel candidate_experiences di database.
    Menyimpan riwayat pengalaman kerja kandidat yang sudah diparse secara terstruktur.
    """

    __tablename__ = "candidate_experiences"

    # ── Primary Key ────────────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ── Foreign Key ────────────────────────────────────────────────────────────
    candidate_profile_id = Column(
        Integer,
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Data Pengalaman Kerja ─────────────────────────────────────────────────
    company_name     = Column(String(255), nullable=True)
    job_title        = Column(String(255), nullable=True)
    employment_type  = Column(String(100), nullable=True)
    location_text    = Column(String(255), nullable=True)
    start_date_text  = Column(String(100), nullable=True)
    end_date_text    = Column(String(100), nullable=True)
    is_current       = Column(Boolean, nullable=False, server_default="0")
    duration_text    = Column(String(100), nullable=True)
    description_text = Column(Text, nullable=True)
    sort_order       = Column(Integer, nullable=True, server_default="0")

    # ── Timestamps ─────────────────────────────────────────────────────────────
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # ── Relationship ───────────────────────────────────────────────────────────
    candidate_profile = relationship("CandidateProfileModel", back_populates="experiences")

    def __repr__(self)-> str:
        return (
            f"<CandidateExperienceModel"
            f"(id={self.id}, company='{self.company_name}', "
            f"job_title='{self.job_title}', start='{self.start_date_text}', "
            f"end='{self.end_date_text}', is_current={self.is_current})>"
        )
"""
ORM Model: candidate_educations
Layer   : Infrastructure > Persistence > Models
Fungsi  : Mapping tabel candidate_educations ke SQLAlchemy ORM
Phase   : 3 - Structured Candidate Data
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from config.database import Base
class CandidateEducationModel(Base):
    """
    Representasi tabel candidate_educations di database.
    Menyimpan riwayat pendidikan kandidat yang sudah diparse secara terstruktur.
    """

    __tablename__ = "candidate_educations"

    # ── Primary Key ────────────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ── Foreign Key ────────────────────────────────────────────────────────────
    candidate_profile_id = Column(
        Integer,
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Data Pendidikan ────────────────────────────────────────────────────────
    institution_name = Column(String(255), nullable=True)
    degree_name      = Column(String(255), nullable=True)
    major_name       = Column(String(255), nullable=True)
    education_level  = Column(String(50),  nullable=True)
    start_date_text  = Column(String(100), nullable=True)
    end_date_text    = Column(String(100), nullable=True)
    gpa_text         = Column(String(50), nullable=True)
    description_text = Column(Text, nullable=True)
    sort_order       = Column(Integer, nullable=True, server_default="0")

    # ── Timestamps ─────────────────────────────────────────────────────────────
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # ── Relationship ───────────────────────────────────────────────────────────
    candidate_profile = relationship("CandidateProfileModel", back_populates="educations")

    def __repr__(self)-> str:
        return (
            f"<CandidateEducationModel"
            f"(id={self.id}, institution='{self.institution_name}', "
            f"degree='{self.degree_name}', major='{self.major_name}', "
            f"start='{self.start_date_text}', end='{self.end_date_text}', "
            f"gpa='{self.gpa_text}')>"
        )
"""
ORM Model: candidate_certifications
Layer   : Infrastructure > Persistence > Models
Fungsi  : Mapping tabel candidate_certifications ke SQLAlchemy ORM
Phase   : 3 - Structured Candidate Data
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from config.database import Base
class CandidateCertificationModel(Base):
    """
    Representasi tabel candidate_certifications di database.
    Menyimpan riwayat sertifikasi kandidat yang sudah diparse secara terstruktur.
    """

    __tablename__ = "candidate_certifications"

    # ── Primary Key ────────────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ── Foreign Key ────────────────────────────────────────────────────────────
    candidate_profile_id = Column(
        Integer,
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Data Sertifikasi ───────────────────────────────────────────────────────
    certification_name = Column(String(255), nullable=True)
    issuer_name = Column(String(255), nullable=True)
    issue_date_text = Column(String(100), nullable=True)
    expiration_date_text = Column(String(100), nullable=True)
    credential_id = Column(String(255), nullable=True)
    credential_url = Column(String(500), nullable=True)
    description_text = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=True, server_default="0")

    # ── Timestamps ─────────────────────────────────────────────────────────────
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # ── Relationship ───────────────────────────────────────────────────────────
    candidate_profile = relationship("CandidateProfileModel", back_populates="certifications")

    def __repr__(self)-> str:
        return (
            f"<CandidateCertificationModel"
            f"(id={self.id}, name='{self.certification_name}', "
            f"issuer='{self.issuer_name}', "
            f"issue_date='{self.issue_date_text}', "
            f"expiration_date='{self.expiration_date_text}')>"
        ) 
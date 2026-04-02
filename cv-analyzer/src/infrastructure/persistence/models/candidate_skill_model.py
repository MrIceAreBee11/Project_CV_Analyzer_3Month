"""
ORM Model: candidate_skills
Layer   : Infrastructure > Persistence > Models
Fungsi  : Mapping tabel candidate_skills ke SQLAlchemy ORM
Phase   : 2 - Basic Parser
"""

from sqlalchemy import (
    Column, Integer, String, Text, Float,
    Boolean, DateTime, ForeignKey, func
)
from sqlalchemy.orm import relationship
from config.database import Base


class CandidateSkillModel(Base):
    """
    Representasi tabel candidate_skills di database.
    Menyimpan skill hasil ekstraksi dari CV kandidat.
    """

    __tablename__ = "candidate_skills"

    # ── Primary Key ────────────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ── Foreign Key ────────────────────────────────────────────────────────────
    candidate_profile_id = Column(
        Integer,
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False
    )

    # ── Data Skill ─────────────────────────────────────────────────────────────
    skill_name = Column(String(255), nullable=False)
    skill_category = Column(String(100), nullable=True)   # contoh: backend, frontend, devops
    source_text = Column(Text, nullable=True)             # potongan teks asal skill ditemukan
    source_section = Column(String(100), nullable=True)   # contoh: skills, experience, education
    confidence_score = Column(Float, nullable=True)       # 0.0 - 1.0
    is_primary = Column(Boolean, nullable=False, default=False)

    # ── Timestamps ─────────────────────────────────────────────────────────────
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    candidate_profile = relationship(
        "CandidateProfileModel",
        back_populates="skills"
    )

    def __repr__(self) -> str:
        return (
            f"<CandidateSkillModel "
            f"id={self.id} "
            f"skill='{self.skill_name}' "
            f"category='{self.skill_category}'>"
        )
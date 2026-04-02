"""
ORM Model: skill_dictionaries
Layer   : Infrastructure > Persistence > Models
Fungsi  : Mapping tabel skill_dictionaries ke SQLAlchemy ORM
Phase   : 2 - Basic Parser
Catatan : Tabel ini adalah master data dictionary skill
          yang digunakan oleh skills_parser untuk mencocokkan
          skill dari raw OCR text.
"""

from sqlalchemy import (
    Column, Integer, String, Text,
    Boolean, DateTime, func
)
from config.database import Base


class SkillDictionaryModel(Base):
    """
    Representasi tabel skill_dictionaries di database.
    Master data dictionary skill untuk proses skill extraction.
    """

    __tablename__ = "skill_dictionaries"

    # ── Primary Key ────────────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ── Data Skill ─────────────────────────────────────────────────────────────
    skill_name = Column(String(255), nullable=False, unique=True)
    normalized_skill_name = Column(String(255), nullable=False)  # lowercase, stripped
    category = Column(String(100), nullable=True)   # contoh: backend, frontend, database, devops

    # ── Aliases ────────────────────────────────────────────────────────────────
    # Disimpan sebagai JSON string
    # contoh: '["js", "javascript", "ecmascript"]'
    aliases_json = Column(Text, nullable=True)

    # ── Status ─────────────────────────────────────────────────────────────────
    is_active = Column(Boolean, nullable=False, default=True)

    # ── Timestamps ─────────────────────────────────────────────────────────────
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<SkillDictionaryModel "
            f"id={self.id} "
            f"skill='{self.skill_name}' "
            f"category='{self.category}' "
            f"active={self.is_active}>"
        )
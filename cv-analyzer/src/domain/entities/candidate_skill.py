"""
Entity: CandidateSkill
Layer : Domain > Entities
Fungsi: Representasi satu skill yang berhasil diekstrak dari CV
Phase : 2 - Basic Parser

Aturan domain:
- Entity ini TIDAK boleh import dari infrastructure atau framework apapun
- confidence_score antara 0.0 sampai 1.0
- skill_name tidak boleh kosong
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CandidateSkill:
    """
    Representasi satu skill hasil ekstraksi dari CV kandidat.
    Setiap skill memiliki informasi dari section mana skill itu ditemukan.
    """

    # ── Primary Identity ───────────────────────────────────────────────────────
    id: Optional[int] = None

    # ── Relasi ke Candidate Profile ────────────────────────────────────────────
    candidate_profile_id: Optional[int] = None

    # ── Data Skill ─────────────────────────────────────────────────────────────
    skill_name: Optional[str] = None
    skill_category: Optional[str] = None    # backend, frontend, database, devops, dll
    source_text: Optional[str] = None       # potongan teks asli tempat skill ditemukan
    source_section: Optional[str] = None    # skills, experience, education, dll
    confidence_score: Optional[float] = None  # 0.0 - 1.0
    is_primary: bool = False                # True jika skill utama kandidat

    # ── Timestamps ─────────────────────────────────────────────────────────────
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # ── Domain Methods ─────────────────────────────────────────────────────────
    def is_high_confidence(self) -> bool:
        """
        Cek apakah skill ini ditemukan dengan confidence tinggi.
        Threshold: >= 0.8
        """
        if self.confidence_score is None:
            return False
        return self.confidence_score >= 0.8

    def is_valid(self) -> bool:
        """Skill dianggap valid jika memiliki nama."""
        return (
            self.skill_name is not None
            and len(self.skill_name.strip()) > 0
        )

    def __repr__(self) -> str:
        return (
            f"<CandidateSkill "
            f"id={self.id} "
            f"skill='{self.skill_name}' "
            f"category='{self.skill_category}' "
            f"confidence={self.confidence_score}>"
        )
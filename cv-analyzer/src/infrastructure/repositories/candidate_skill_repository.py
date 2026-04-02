"""
Repository : CandidateSkillRepository
Layer      : Infrastructure > Repositories
Fungsi     : Implementasi konkret ICandidateSkillRepository.
             Menangani semua operasi database untuk tabel candidate_skills
             menggunakan SQLAlchemy ORM.
Phase      : 2 - Basic Parser
"""

from typing import List
from sqlalchemy.orm import Session

from src.app.interfaces.repositories.i_candidate_skill_repository import (
    ICandidateSkillRepository
)
from src.domain.entities.candidate_skill import CandidateSkill
from src.infrastructure.persistence.models.candidate_skill_model import (
    CandidateSkillModel
)


class CandidateSkillRepository(ICandidateSkillRepository):
    """
    Implementasi repository candidate skill menggunakan SQLAlchemy.
    """

    def __init__(self, db: Session):
        """
        Args:
            db: SQLAlchemy session yang di-inject dari luar
        """
        self.db = db

    # ── Save Many ──────────────────────────────────────────────────────────────

    def save_many(self, skills: List[CandidateSkill]) -> List[CandidateSkill]:
        """
        Bulk insert semua skill sekaligus.
        Lebih efisien daripada insert satu per satu.
        """
        if not skills:
            return []

        models = [self._to_model(skill) for skill in skills]

        self.db.add_all(models)
        self.db.flush()

        return [self._to_entity(m) for m in models]

    # ── Find ───────────────────────────────────────────────────────────────────

    def find_by_candidate_profile_id(
        self,
        candidate_profile_id: int
    ) -> List[CandidateSkill]:
        """Ambil semua skill milik satu candidate profile."""
        models = (
            self.db.query(CandidateSkillModel)
            .filter(
                CandidateSkillModel.candidate_profile_id == candidate_profile_id
            )
            .order_by(
                CandidateSkillModel.confidence_score.desc()
            )
            .all()
        )
        return [self._to_entity(m) for m in models]

    # ── Delete ─────────────────────────────────────────────────────────────────

    def delete_by_candidate_profile_id(
        self,
        candidate_profile_id: int
    ) -> bool:
        """
        Hapus semua skill milik satu candidate profile (hard delete).
        Dipakai saat reparse agar skill lama diganti skill baru.
        """
        self.db.query(CandidateSkillModel).filter(
            CandidateSkillModel.candidate_profile_id == candidate_profile_id
        ).delete(synchronize_session=False)

        self.db.flush()
        return True

    # ── Mapper ─────────────────────────────────────────────────────────────────

    def _to_model(self, skill: CandidateSkill) -> CandidateSkillModel:
        """Konversi domain entity → ORM model."""
        return CandidateSkillModel(
            candidate_profile_id=skill.candidate_profile_id,
            skill_name=skill.skill_name,
            skill_category=skill.skill_category,
            source_text=skill.source_text,
            source_section=skill.source_section,
            confidence_score=skill.confidence_score,
            is_primary=skill.is_primary,
        )

    def _to_entity(self, model: CandidateSkillModel) -> CandidateSkill:
        """Konversi ORM model → domain entity."""
        return CandidateSkill(
            id=model.id,
            candidate_profile_id=model.candidate_profile_id,
            skill_name=model.skill_name,
            skill_category=model.skill_category,
            source_text=model.source_text,
            source_section=model.source_section,
            confidence_score=model.confidence_score,
            is_primary=model.is_primary,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
"""
Repository : CandidateExperienceRepository
Layer      : Infrastructure > Repositories
Fungsi     : Implementasi konkret ICandidateExperienceRepository.
             Menangani semua operasi database untuk tabel candidate_experiences.
Phase      : 3 - Structured Candidate Data
"""

from typing import List
from sqlalchemy.orm import Session

from src.app.interfaces.repositories.i_candidate_experience_repository import (
    ICandidateExperienceRepository
)
from src.domain.entities.candidate_experience import CandidateExperience
from src.infrastructure.persistence.models.candidate_experience_model import (
    CandidateExperienceModel
)


class CandidateExperienceRepository(ICandidateExperienceRepository):
    """
    Implementasi repository candidate experience menggunakan SQLAlchemy.
    Bertanggung jawab HANYA pada akses database.
    """

    def __init__(self, db: Session):
        self.db = db

    # ── Save Many ──────────────────────────────────────────────────────────────

    def save_many(
        self, experiences: List[CandidateExperience]
    ) -> List[CandidateExperience]:
        """Bulk insert semua experience sekaligus."""
        if not experiences:
            return []

        models = [self._to_model(exp) for exp in experiences]
        self.db.add_all(models)
        self.db.flush()

        return [self._to_entity(m) for m in models]

    # ── Find ───────────────────────────────────────────────────────────────────

    def find_by_candidate_profile_id(
        self, candidate_profile_id: int
    ) -> List[CandidateExperience]:
        """Ambil semua experience milik satu candidate profile."""
        models = (
            self.db.query(CandidateExperienceModel)
            .filter(
                CandidateExperienceModel.candidate_profile_id == candidate_profile_id
            )
            .order_by(CandidateExperienceModel.sort_order.asc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    # ── Delete ─────────────────────────────────────────────────────────────────

    def delete_by_candidate_profile_id(
        self, candidate_profile_id: int
    ) -> bool:
        """Hapus semua experience milik satu candidate profile (untuk reparse)."""
        self.db.query(CandidateExperienceModel).filter(
            CandidateExperienceModel.candidate_profile_id == candidate_profile_id
        ).delete(synchronize_session=False)
        self.db.flush()
        return True

    # ── Mapper ─────────────────────────────────────────────────────────────────

    def _to_model(self, exp: CandidateExperience) -> CandidateExperienceModel:
        """Konversi domain entity → ORM model."""
        return CandidateExperienceModel(
            candidate_profile_id=exp.candidate_profile_id,
            company_name=exp.company_name,
            job_title=exp.job_title,
            employment_type=exp.employment_type,
            location_text=exp.location_text,
            start_date_text=exp.start_date_text,
            end_date_text=exp.end_date_text,
            is_current=exp.is_current,
            duration_text=exp.duration_text,
            description_text=exp.description_text,
            sort_order=exp.sort_order,
        )

    def _to_entity(self, model: CandidateExperienceModel) -> CandidateExperience:
        """Konversi ORM model → domain entity."""
        return CandidateExperience(
            id=model.id,
            candidate_profile_id=model.candidate_profile_id,
            company_name=model.company_name,
            job_title=model.job_title,
            employment_type=model.employment_type,
            location_text=model.location_text,
            start_date_text=model.start_date_text,
            end_date_text=model.end_date_text,
            is_current=model.is_current,
            duration_text=model.duration_text,
            description_text=model.description_text,
            sort_order=model.sort_order,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
"""
Repository : CandidateEducationRepository
Layer      : Infrastructure > Repositories
Fungsi     : Implementasi konkret ICandidateEducationRepository.
             Menangani semua operasi database untuk tabel candidate_educations.
Phase      : 3 - Structured Candidate Data
"""

from typing import List
from sqlalchemy.orm import Session

from src.app.interfaces.repositories.i_candidate_education_repository import (
    ICandidateEducationRepository
)
from src.domain.entities.candidate_education import CandidateEducation
from src.infrastructure.persistence.models.candidate_education_model import (
    CandidateEducationModel
)


class CandidateEducationRepository(ICandidateEducationRepository):
    """
    Implementasi repository candidate education menggunakan SQLAlchemy.
    """

    def __init__(self, db: Session):
        self.db = db

    # ── Save Many ──────────────────────────────────────────────────────────────

    def save_many(
        self, educations: List[CandidateEducation]
    ) -> List[CandidateEducation]:
        """Bulk insert semua education sekaligus."""
        if not educations:
            return []

        models = [self._to_model(edu) for edu in educations]
        self.db.add_all(models)
        self.db.flush()

        return [self._to_entity(m) for m in models]

    # ── Find ───────────────────────────────────────────────────────────────────

    def find_by_candidate_profile_id(
        self, candidate_profile_id: int
    ) -> List[CandidateEducation]:
        """Ambil semua education milik satu candidate profile."""
        models = (
            self.db.query(CandidateEducationModel)
            .filter(
                CandidateEducationModel.candidate_profile_id == candidate_profile_id
            )
            .order_by(CandidateEducationModel.sort_order.asc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    # ── Delete ─────────────────────────────────────────────────────────────────

    def delete_by_candidate_profile_id(
        self, candidate_profile_id: int
    ) -> bool:
        """Hapus semua education milik satu candidate profile (untuk reparse)."""
        self.db.query(CandidateEducationModel).filter(
            CandidateEducationModel.candidate_profile_id == candidate_profile_id
        ).delete(synchronize_session=False)
        self.db.flush()
        return True

    # ── Mapper ─────────────────────────────────────────────────────────────────

    def _to_model(self, edu: CandidateEducation) -> CandidateEducationModel:
        """Konversi domain entity → ORM model."""
        return CandidateEducationModel(
            candidate_profile_id=edu.candidate_profile_id,
            institution_name=edu.institution_name,
            degree_name=edu.degree_name,
            major_name=edu.major_name,
            education_level=edu.education_level,
            start_date_text=edu.start_date_text,
            end_date_text=edu.end_date_text,
            gpa_text=edu.gpa_text,
            description_text=edu.description_text,
            sort_order=edu.sort_order,
        )

    def _to_entity(self, model: CandidateEducationModel) -> CandidateEducation:
        """Konversi ORM model → domain entity."""
        return CandidateEducation(
            id=model.id,
            candidate_profile_id=model.candidate_profile_id,
            institution_name=model.institution_name,
            degree_name=model.degree_name,
            major_name=model.major_name,
            education_level=model.education_level,
            start_date_text=model.start_date_text,
            end_date_text=model.end_date_text,
            gpa_text=model.gpa_text,
            description_text=model.description_text,
            sort_order=model.sort_order,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
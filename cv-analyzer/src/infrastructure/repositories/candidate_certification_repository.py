"""
Repository : CandidateCertificationRepository
Layer      : Infrastructure > Repositories
Fungsi     : Implementasi konkret ICandidateCertificationRepository.
             Menangani semua operasi database untuk tabel candidate_certifications.
Phase      : 3 - Structured Candidate Data
"""

from typing import List
from sqlalchemy.orm import Session

from src.app.interfaces.repositories.i_candidate_certification_repository import (
    ICandidateCertificationRepository
)
from src.domain.entities.candidate_certification import CandidateCertification
from src.infrastructure.persistence.models.candidate_certification_model import (
    CandidateCertificationModel
)


class CandidateCertificationRepository(ICandidateCertificationRepository):
    """
    Implementasi repository candidate certification menggunakan SQLAlchemy.
    """

    def __init__(self, db: Session):
        self.db = db

    # ── Save Many ──────────────────────────────────────────────────────────────

    def save_many(
        self, certifications: List[CandidateCertification]
    ) -> List[CandidateCertification]:
        """Bulk insert semua certification sekaligus."""
        if not certifications:
            return []

        models = [self._to_model(cert) for cert in certifications]
        self.db.add_all(models)
        self.db.flush()

        return [self._to_entity(m) for m in models]

    # ── Find ───────────────────────────────────────────────────────────────────

    def find_by_candidate_profile_id(
        self, candidate_profile_id: int
    ) -> List[CandidateCertification]:
        """Ambil semua certification milik satu candidate profile."""
        models = (
            self.db.query(CandidateCertificationModel)
            .filter(
                CandidateCertificationModel.candidate_profile_id == candidate_profile_id
            )
            .order_by(CandidateCertificationModel.created_at.asc())
            .all()
        )
        return [self._to_entity(m) for m in models]

    # ── Delete ─────────────────────────────────────────────────────────────────

    def delete_by_candidate_profile_id(
        self, candidate_profile_id: int
    ) -> bool:
        """Hapus semua certification milik satu candidate profile (untuk reparse)."""
        self.db.query(CandidateCertificationModel).filter(
            CandidateCertificationModel.candidate_profile_id == candidate_profile_id
        ).delete(synchronize_session=False)
        self.db.flush()
        return True

    # ── Mapper ─────────────────────────────────────────────────────────────────

    def _to_model(
        self, cert: CandidateCertification
    ) -> CandidateCertificationModel:
        """Konversi domain entity → ORM model."""
        return CandidateCertificationModel(
            candidate_profile_id=cert.candidate_profile_id,
            certification_name=cert.certification_name,
            issuer_name=cert.issuer_name,
            issue_date_text=cert.issue_date_text,
            expiration_date_text=cert.expiration_date_text,
            credential_id=cert.credential_id,
            credential_url=cert.credential_url,
        )

    def _to_entity(
        self, model: CandidateCertificationModel
    ) -> CandidateCertification:
        """Konversi ORM model → domain entity."""
        return CandidateCertification(
            id=model.id,
            candidate_profile_id=model.candidate_profile_id,
            certification_name=model.certification_name,
            issuer_name=model.issuer_name,
            issue_date_text=model.issue_date_text,
            expiration_date_text=model.expiration_date_text,
            credential_id=model.credential_id,
            credential_url=model.credential_url,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
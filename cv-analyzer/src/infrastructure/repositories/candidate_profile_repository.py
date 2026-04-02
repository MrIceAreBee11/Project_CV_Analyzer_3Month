
"""
Repository : CandidateProfileRepository
Layer      : Infrastructure > Repositories
Fungsi     : Implementasi konkret ICandidateProfileRepository.
             Menangani semua operasi database untuk tabel candidate_profiles
             menggunakan SQLAlchemy ORM.
Phase      : 2 - Basic Parser
"""

import uuid as uuid_lib
from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from src.app.interfaces.repositories.i_candidate_profile_repository import (
    ICandidateProfileRepository
)
from src.domain.entities.candidate_profile import CandidateProfile
from src.infrastructure.persistence.models.candidate_profile_model import (
    CandidateProfileModel
)


class CandidateProfileRepository(ICandidateProfileRepository):
    """
    Implementasi repository candidate profile menggunakan SQLAlchemy.
    Bertanggung jawab HANYA pada akses database — tidak ada business logic.
    """

    def __init__(self, db: Session):
        """
        Args:
            db: SQLAlchemy session yang di-inject dari luar
        """
        self.db = db

    # ── Save ───────────────────────────────────────────────────────────────────

    def save(self, candidate_profile: CandidateProfile) -> CandidateProfile:
        """
        Simpan candidate profile baru ke database.
        UUID di-generate otomatis jika belum ada.
        """
        model = CandidateProfileModel(
            uuid=candidate_profile.uuid or str(uuid_lib.uuid4()),
            cv_document_id=candidate_profile.cv_document_id,
            full_name=candidate_profile.full_name,
            email=candidate_profile.email,
            phone_number=candidate_profile.phone_number,
            alternate_phone_number=candidate_profile.alternate_phone_number,
            current_location=candidate_profile.current_location,
            address_text=candidate_profile.address_text,
            professional_summary=candidate_profile.professional_summary,
            date_of_birth_text=candidate_profile.date_of_birth_text,
            total_experience_text=candidate_profile.total_experience_text,
            estimated_total_experience_months=(
                candidate_profile.estimated_total_experience_months
            ),
            latest_job_title=candidate_profile.latest_job_title,
            latest_company_name=candidate_profile.latest_company_name,
            linkedin_url=candidate_profile.linkedin_url,
            github_url=candidate_profile.github_url,
            portfolio_url=candidate_profile.portfolio_url,
            raw_text=candidate_profile.raw_text,
            parser_version=candidate_profile.parser_version,
            parser_status=candidate_profile.parser_status,
            parser_notes=candidate_profile.parser_notes,
        )

        self.db.add(model)
        self.db.flush()  # dapatkan id tanpa commit dulu

        return self._to_entity(model)

    # ── Update ─────────────────────────────────────────────────────────────────

    def update(self, candidate_profile: CandidateProfile) -> CandidateProfile:
        """
        Update candidate profile yang sudah ada.
        """
        model = self.db.query(CandidateProfileModel).filter(
            CandidateProfileModel.id == candidate_profile.id
        ).first()

        if not model:
            raise Exception(f"Candidate profile with id {candidate_profile.id} not found")

        model.full_name                        = candidate_profile.full_name  # type: ignore[assignment]
        model.email                            = candidate_profile.email  # type: ignore[assignment]
        model.phone_number                     = candidate_profile.phone_number # type: ignore[assignment]
        model.alternate_phone_number           = candidate_profile.alternate_phone_number # type: ignore[assignment]
        model.current_location                 = candidate_profile.current_location # type: ignore[assignment]
        model.address_text                     = candidate_profile.address_text # type: ignore[assignment]
        model.professional_summary             = candidate_profile.professional_summary # type: ignore[assignment]
        model.date_of_birth_text               = candidate_profile.date_of_birth_text # type: ignore[assignment]
        model.total_experience_text            = candidate_profile.total_experience_text # type: ignore[assignment]
        model.estimated_total_experience_months = ( # type: ignore[assignment]
            candidate_profile.estimated_total_experience_months 
        )
        model.latest_job_title                 = candidate_profile.latest_job_title # type: ignore[assignment]
        model.latest_company_name              = candidate_profile.latest_company_name # type: ignore[assignment]
        model.linkedin_url                     = candidate_profile.linkedin_url # type: ignore[assignment]
        model.github_url                       = candidate_profile.github_url # type: ignore[assignment]
        model.portfolio_url                    = candidate_profile.portfolio_url # type: ignore[assignment]
        model.raw_text                         = candidate_profile.raw_text # type: ignore[assignment]
        model.parser_version                   = candidate_profile.parser_version # type: ignore[assignment]
        model.parser_status                    = candidate_profile.parser_status # type: ignore[assignment]
        model.parser_notes                     = candidate_profile.parser_notes  # type: ignore[assignment]

        self.db.flush()

        return self._to_entity(model)

    # ── Find ───────────────────────────────────────────────────────────────────

    def find_by_id(self, profile_id: int) -> Optional[CandidateProfile]:
        model = (
            self.db.query(CandidateProfileModel)
            .filter(
                CandidateProfileModel.id == profile_id,
                CandidateProfileModel.deleted_at.is_(None)
            )
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_uuid(self, uuid: str) -> Optional[CandidateProfile]:
        model = (
            self.db.query(CandidateProfileModel)
            .filter(
                CandidateProfileModel.uuid == uuid,
                CandidateProfileModel.deleted_at.is_(None)
            )
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_cv_document_id(
        self, cv_document_id: int
    ) -> Optional[CandidateProfile]:
        model = (
            self.db.query(CandidateProfileModel)
            .filter(
                CandidateProfileModel.cv_document_id == cv_document_id,
                CandidateProfileModel.deleted_at.is_(None)
            )
            .first()
        )
        return self._to_entity(model) if model else None

    def find_all(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> List[CandidateProfile]:
        models = (
            self.db.query(CandidateProfileModel)
            .filter(CandidateProfileModel.deleted_at.is_(None))
            .order_by(CandidateProfileModel.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [self._to_entity(m) for m in models]

    # ── Delete ─────────────────────────────────────────────────────────────────

    def delete_by_id(self, profile_id: int) -> bool:
        """Soft delete — isi deleted_at, tidak hapus row."""
        model = (
            self.db.query(CandidateProfileModel)
            .filter(CandidateProfileModel.id == profile_id)
            .first()
        )
        if not model:
            return False

        model.deleted_at = datetime.utcnow() # type: ignore[assignment]
        self.db.flush()
        return True

    # ── Mapper ─────────────────────────────────────────────────────────────────
    def _to_entity(self, model: CandidateProfileModel) -> CandidateProfile:
        """
        Konversi ORM model → domain entity.
        Pemisahan ini memastikan domain layer tidak tahu soal ORM.
        """
        return CandidateProfile(
            id=model.id, # type: ignore[assignment]
            uuid=model.uuid, # type: ignore[assignment]
            cv_document_id=model.cv_document_id, # type: ignore[assignment]
            full_name=model.full_name, # type: ignore[assignment]
            email=model.email, # type: ignore[assignment]
            phone_number=model.phone_number, # type: ignore[assignment]
            alternate_phone_number=model.alternate_phone_number, # type: ignore[assignment]
            current_location=model.current_location, # type: ignore[assignment]
            address_text=model.address_text, # type: ignore[assignment]
            professional_summary=model.professional_summary, # type: ignore[assignment]
            date_of_birth_text=model.date_of_birth_text, # type: ignore[assignment]
            total_experience_text=model.total_experience_text,  # type: ignore[assignment]
            estimated_total_experience_months=(
                model.estimated_total_experience_months # type: ignore[assignment]
            ),
            latest_job_title=model.latest_job_title, # type: ignore[assignment]
            latest_company_name=model.latest_company_name, # type: ignore[assignment]
            linkedin_url=model.linkedin_url, # type: ignore[assignment]
            github_url=model.github_url, # type: ignore[assignment]
            portfolio_url=model.portfolio_url, # type: ignore[assignment]
            raw_text=model.raw_text, # type: ignore[assignment]
            parser_version=model.parser_version, # type: ignore[assignment]
            parser_status=model.parser_status, # type: ignore[assignment]
            parser_notes=model.parser_notes, # type: ignore[assignment]
            created_at=model.created_at, # type: ignore[assignment]
            updated_at=model.updated_at, # type: ignore[assignment]
            deleted_at=model.deleted_at, # type: ignore[assignment]
        )
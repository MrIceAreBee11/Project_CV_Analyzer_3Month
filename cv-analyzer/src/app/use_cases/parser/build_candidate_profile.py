"""
Use Case : BuildCandidateProfile
Layer    : App > Use Cases > Parser
Fungsi   : Orkestrasi proses parsing raw OCR text menjadi
           candidate profile yang terstruktur.
Phase    : 2 - Basic Parser

Alur kerja:
1. Ambil cv_document berdasarkan cv_document_id
2. Ambil raw OCR text dari cv_ocr_results
3. Jalankan identity parser → dapat data identitas
4. Simpan candidate profile ke database
5. Jalankan skills parser → dapat daftar skill
6. Simpan skills ke database
7. Update status cv_document menjadi parsing_completed
8. Return hasil profile lengkap
"""

from sqlalchemy.orm import Session

from src.app.interfaces.repositories.i_cv_document_repository import (
    ICvDocumentRepository
)
from src.app.interfaces.repositories.i_cv_ocr_result_repository import (
    ICvOcrResultRepository
)
from src.app.interfaces.repositories.i_candidate_profile_repository import (
    ICandidateProfileRepository
)
from src.app.interfaces.repositories.i_candidate_skill_repository import (
    ICandidateSkillRepository
)
from src.app.interfaces.services.i_candidate_parser_service import (
    ICandidateParserService
)
from src.domain.entities.candidate_profile import CandidateProfile
from src.app.dto.parser.candidate_profile_dto import (
    BuildCandidateProfileResponse,
    CandidateProfileResponse,
    CandidateSkillResponse,
)


class BuildCandidateProfile:
    """
    Use case untuk membangun candidate profile dari hasil OCR.
    Menggunakan dependency injection — tidak import implementasi langsung.
    """

    def __init__(
        self,
        cv_document_repository: ICvDocumentRepository,
        cv_ocr_result_repository: ICvOcrResultRepository,
        candidate_profile_repository: ICandidateProfileRepository,
        candidate_skill_repository: ICandidateSkillRepository,
        parser_service: ICandidateParserService,
    ):
        self._cv_doc_repo      = cv_document_repository
        self._ocr_result_repo  = cv_ocr_result_repository
        self._profile_repo     = candidate_profile_repository
        self._skill_repo       = candidate_skill_repository
        self._parser           = parser_service

    # ── Execute ────────────────────────────────────────────────────────────────

    def execute(self, cv_document_id: int) -> BuildCandidateProfileResponse:
        """
        Jalankan proses build candidate profile.

        Args:
            cv_document_id: ID dokumen CV yang akan di-parse

        Returns:
            BuildCandidateProfileResponse berisi hasil profile dan skill
        """

        # ── 1. Validasi: cv_document harus ada ────────────────────────────────
        cv_document = self._cv_doc_repo.find_by_id(cv_document_id)
        if not cv_document:
            return BuildCandidateProfileResponse(
                success=False,
                message=f"CV Document id={cv_document_id} tidak ditemukan.",
            )

        # ── 2. Validasi: OCR harus sudah selesai ──────────────────────────────
        if cv_document.status not in ("ocr_completed", "parsing_failed"):
            return BuildCandidateProfileResponse(
                success=False,
                message=(
                    f"CV Document belum siap di-parse. "
                    f"Status saat ini: '{cv_document.status}'. "
                    f"Status yang dibutuhkan: 'ocr_completed'."
                ),
            )

        # ── 3. Ambil raw OCR text ──────────────────────────────────────────────
        raw_text = self._get_merged_ocr_text(cv_document_id)
        if not raw_text:
            return BuildCandidateProfileResponse(
                success=False,
                message="Tidak ada OCR text yang tersedia untuk dokumen ini.",
            )

        # ── 4. Cek apakah profile sudah pernah dibuat (untuk reparse) ─────────
        existing_profile = self._profile_repo.find_by_cv_document_id(
            cv_document_id
        )

        try:
            # ── 5. Extract identitas dari raw text ────────────────────────────
            parsed_profile = self._parser.extract_identity(raw_text)
            parsed_profile.cv_document_id = cv_document_id
            parsed_profile.parser_status  = "completed"

            # ── 6. Simpan atau update candidate profile ────────────────────────
            if existing_profile:
                parsed_profile.id   = existing_profile.id
                parsed_profile.uuid = existing_profile.uuid
                saved_profile = self._profile_repo.update(parsed_profile)

                # Hapus skill lama sebelum insert skill baru
                self._skill_repo.delete_by_candidate_profile_id(
                    existing_profile.id  # type: ignore[arg-type]
                )
            else:
                saved_profile = self._profile_repo.save(parsed_profile)

            # ── 7. Extract dan simpan skills ───────────────────────────────────
            skills = self._parser.extract_skills(
                raw_text=raw_text,
                candidate_profile_id=saved_profile.id,  # type: ignore[arg-type]
            )
            saved_skills = []
            if skills:
                saved_skills = self._skill_repo.save_many(skills)

            # ── 8. Update status cv_document ───────────────────────────────────
            cv_document.status = "parsing_completed"
            self._cv_doc_repo.update(cv_document)

            # ── 9. Susun response ──────────────────────────────────────────────
            skill_responses = [
                CandidateSkillResponse(
                    id=s.id,
                    skill_name=s.skill_name,
                    skill_category=s.skill_category,
                    source_section=s.source_section,
                    confidence_score=s.confidence_score,
                    is_primary=s.is_primary,
                )
                for s in saved_skills
            ]

            profile_response = CandidateProfileResponse(
                id=saved_profile.id,
                uuid=saved_profile.uuid,
                cv_document_id=saved_profile.cv_document_id,
                full_name=saved_profile.full_name,
                email=saved_profile.email,
                phone_number=saved_profile.phone_number,
                current_location=saved_profile.current_location,
                professional_summary=saved_profile.professional_summary,
                latest_job_title=saved_profile.latest_job_title,
                latest_company_name=saved_profile.latest_company_name,
                linkedin_url=saved_profile.linkedin_url,
                github_url=saved_profile.github_url,
                portfolio_url=saved_profile.portfolio_url,
                parser_version=saved_profile.parser_version,
                parser_status=saved_profile.parser_status,
                parser_notes=saved_profile.parser_notes,
                skills=skill_responses,
            )

            return BuildCandidateProfileResponse(
                success=True,
                message="Candidate profile berhasil dibangun.",
                profile=profile_response,
                total_skills_found=len(saved_skills),
            )

        except Exception as e:
            # Update status jadi parsing_failed jika ada error
            cv_document.status = "parsing_failed"
            self._cv_doc_repo.update(cv_document)

            return BuildCandidateProfileResponse(
                success=False,
                message=f"Parsing gagal: {str(e)}",
            )

    # ── Private ────────────────────────────────────────────────────────────────

    def _get_merged_ocr_text(self, cv_document_id: int) -> str:
        """
        Ambil dan gabungkan semua raw OCR text dari seluruh halaman dokumen.
        Diurutkan berdasarkan page_number.
        """
        ocr_results = self._ocr_result_repo.find_by_cv_document_id(
            cv_document_id
        )

        if not ocr_results:
            return ""

        # Urutkan berdasarkan page_number
        ocr_results.sort(key=lambda x: x.page_number or 0)

        merged = "\n\n".join(
            result.raw_text
            for result in ocr_results
            if result.raw_text and result.raw_text.strip()
        )

        return merged
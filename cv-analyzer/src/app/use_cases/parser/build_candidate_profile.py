"""
Use Case : BuildCandidateProfile
Layer    : App > Use Cases > Parser
Fungsi   : Orkestrasi proses parsing raw OCR text menjadi
           candidate profile yang terstruktur.
Phase    : 2 - Basic Parser
         : 3 - (Update) tambah extract experiences, educations, certifications

Alur kerja:
1. Ambil cv_document berdasarkan cv_document_id
2. Validasi status OCR sudah selesai
3. Ambil raw OCR text
4. Extract identitas → simpan candidate profile
5. Extract skills → simpan
6. Extract experiences → simpan
7. Extract educations → simpan
8. Extract certifications → simpan
9. Update status cv_document → parsing_completed
10. Return hasil lengkap
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
from src.app.interfaces.repositories.i_candidate_experience_repository import (
    ICandidateExperienceRepository
)
from src.app.interfaces.repositories.i_candidate_education_repository import (
    ICandidateEducationRepository
)
from src.app.interfaces.repositories.i_candidate_certification_repository import (
    ICandidateCertificationRepository
)
from src.app.interfaces.services.i_candidate_parser_service import (
    ICandidateParserService
)
from src.domain.entities.candidate_profile import CandidateProfile
from src.app.dto.parser.candidate_profile_dto import (
    BuildCandidateProfileResponse,
    CandidateProfileResponse,
    CandidateSkillResponse,
    CandidateExperienceResponse,
    CandidateEducationResponse,
    CandidateCertificationResponse,
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
        candidate_experience_repository: ICandidateExperienceRepository,
        candidate_education_repository: ICandidateEducationRepository,
        candidate_certification_repository: ICandidateCertificationRepository,

        parser_service: ICandidateParserService,
    ):
        self._cv_doc_repo      = cv_document_repository
        self._ocr_result_repo  = cv_ocr_result_repository
        self._profile_repo     = candidate_profile_repository
        self._skill_repo       = candidate_skill_repository
        self._experience_repo  = candidate_experience_repository
        self._education_repo   = candidate_education_repository
        self._certification_repo = candidate_certification_repository
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
            # ── 5. Extract identitas dari raw text 
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
            saved_skills: list = []
            if skills:
                saved_skills = self._skill_repo.save_many(skills)

            # ── 8. Extract dan simpan experiences ──────────────────────────────
            experiences = self._parser.extract_experiences(
                raw_text=raw_text,
                candidate_profile_id=saved_profile.id,  # type: ignore[arg-type]
            )
            saved_experiences: list = []
            if experiences:
                # kalau re-parse, hapus dulu yang lama
                if existing_profile and existing_profile.id is not None:
                    self._experience_repo.delete_by_candidate_profile_id(
                        existing_profile.id
                    )
                saved_experiences = self._experience_repo.save_many(experiences)

            # ── 9. Extract dan simpan educations ───────────────────────────────
            educations = self._parser.extract_educations(
                raw_text=raw_text,
                candidate_profile_id=saved_profile.id,  # type: ignore[arg-type]
            )
            saved_educations: list = []
            if educations:
                if existing_profile and existing_profile.id is not None:
                    self._education_repo.delete_by_candidate_profile_id(
                        existing_profile.id
                    )
                saved_educations = self._education_repo.save_many(educations)

            # ── 10. Extract dan simpan certifications ──────────────────────────
            certifications = self._parser.extract_certifications(
                raw_text=raw_text,
                candidate_profile_id=saved_profile.id,  # type: ignore[arg-type]
            )
            saved_certifications: list = []
            if certifications:
                if existing_profile and existing_profile.id is not None:
                    self._certification_repo.delete_by_candidate_profile_id(
                        existing_profile.id
                    )
                saved_certifications = self._certification_repo.save_many(
                    certifications
                )

            # ── 11. Update status cv_document ──────────────────────────────────
            cv_document.status = "parsing_completed"  # type: ignore[assignment]
            self._cv_doc_repo.update(cv_document)

            # ── 12. Susun response lengkap ─────────────────────────────────────
            profile_response = self._build_profile_response(
                profile=saved_profile,
                skills=saved_skills,
                experiences=saved_experiences,
                educations=saved_educations,
                certifications=saved_certifications,
            )

            return BuildCandidateProfileResponse(
                success=True,
                message="Candidate profile berhasil dibangun.",
                profile=profile_response,
                total_skills_found=len(saved_skills),
                total_experiences_found=len(saved_experiences),
                total_educations_found=len(saved_educations),
                total_certifications_found=len(saved_certifications),
            )

        except Exception as e:
            # Update status jadi parsing_failed jika ada error
            cv_document.status = "parsing_failed" # type: ignore[assignment]
            self._cv_doc_repo.update(cv_document)

            return BuildCandidateProfileResponse(
                success=False,
                message=f"Parsing gagal: {str(e)}",
            )

    # ── Private : Helpers ────────────────────────────────────────────────────────────────

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

        return "\n\n".join(
            text
            for r in ocr_results
            for text in [str(r.raw_text)] #type: ignore[arg-type]
            if text.strip()  # Hanya gabungkan jika ada teks yang tidak kosong
        )
    def _build_profile_response(
        self,
        profile,
        skills,
        experiences,
        educations,
        certifications,
    ) -> CandidateProfileResponse :
        """Susun CandidateProfileResponse dari semua data yang sudah disimpan."""
        skill_responses = [
            CandidateSkillResponse(
                id=s.id,
                skill_name=s.skill_name,
                skill_category=s.skill_category,
                source_section=s.source_section,
                confidence_score=s.confidence_score,
                is_primary=s.is_primary,
            )
            for s in skills
        ]

        experience_responses = [
            CandidateExperienceResponse(
                id=e.id,
                job_title=e.job_title,
                company_name=e.company_name,
                employment_type=e.employment_type,
                location_text=e.location_text,
                start_date_text=e.start_date_text,
                end_date_text=e.end_date_text,
                is_current=e.is_current,
                duration_text=e.duration_text,
                description_text=e.description_text,
                sort_order=e.sort_order,
            )
            for e in experiences
        ]

        education_responses = [
            CandidateEducationResponse(
                id=edu.id,
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
            for edu in educations
        ]

        certification_responses = [
            CandidateCertificationResponse(
                id=c.id,
                certification_name=c.certification_name,
                issuer_name=c.issuer_name,
                issue_date_text=c.issue_date_text,
                expiration_date_text=c.expiration_date_text,
                credential_id=c.credential_id,
                credential_url=c.credential_url,
            )
            for c in certifications
        ]

        return CandidateProfileResponse(
            id=profile.id,
            uuid=profile.uuid,
            cv_document_id=profile.cv_document_id,
            full_name=profile.full_name,
            email=profile.email,
            phone_number=profile.phone_number,
            current_location=profile.current_location,
            professional_summary=profile.professional_summary,
            latest_job_title=profile.latest_job_title,
            latest_company_name=profile.latest_company_name,
            linkedin_url=profile.linkedin_url,
            github_url=profile.github_url,
            portfolio_url=profile.portfolio_url,
            parser_version=profile.parser_version,
            parser_status=profile.parser_status,
            parser_notes=profile.parser_notes,
            skills=skill_responses,
            experiences=experience_responses,
            educations=education_responses,
            certifications=certification_responses
        )

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.database import get_db
from src.app.dto.parser.candidate_profile_dto import (
    BuildCandidateProfileResponse,
    CandidateProfileResponse,
    CandidateSkillResponse,
)
from src.app.use_cases.parser.build_candidate_profile import (
    BuildCandidateProfile
)

# Infrastructure — repositories
from src.infrastructure.repositories.cv_document_repository import (
    CvDocumentRepository
)
from src.infrastructure.repositories.cv_ocr_result_repository import (
    CvOcrResultRepository
)
from src.infrastructure.repositories.candidate_profile_repository import (
    CandidateProfileRepository
)
from src.infrastructure.repositories.candidate_skill_repository import (
    CandidateSkillRepository
)

# Infrastructure — parser service
from src.infrastructure.parsers.candidate_parser_service import (
    CandidateParserService
)

router = APIRouter(
    prefix="/candidate-profiles",
    tags=["Candidate Profiles"],
)


# ── Dependency Injection ───────────────────────────────────────────────────────

def get_build_use_case(db: Session = Depends(get_db)) -> BuildCandidateProfile:
    """
    Factory function untuk membuat use case BuildCandidateProfile
    dengan semua dependency yang dibutuhkan.
    """
    return BuildCandidateProfile(
        cv_document_repository=CvDocumentRepository(db),
        cv_ocr_result_repository=CvOcrResultRepository(db),
        candidate_profile_repository=CandidateProfileRepository(db),
        candidate_skill_repository=CandidateSkillRepository(db),
        parser_service=CandidateParserService(db),
    )

def get_profile_repository(
    db: Session = Depends(get_db)
) -> CandidateProfileRepository:
    return CandidateProfileRepository(db)

def get_skill_repository(
    db: Session = Depends(get_db)
) -> CandidateSkillRepository:
    return CandidateSkillRepository(db)


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post(
    "/build/{cv_document_id}",
    response_model=BuildCandidateProfileResponse,
    summary="Build candidate profile dari hasil OCR",
    description=(
        "Trigger proses parsing raw OCR text menjadi candidate profile "
        "yang terstruktur. CV Document harus sudah berstatus 'ocr_completed'."
    ),
)
def build_candidate_profile(
    cv_document_id: int,
    use_case: BuildCandidateProfile = Depends(get_build_use_case),
):
    result = use_case.execute(cv_document_id=cv_document_id)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)

    return result


@router.get(
    "/by-document/{cv_document_id}",
    response_model=CandidateProfileResponse,
    summary="Lihat candidate profile berdasarkan cv_document_id",
)
def get_profile_by_document(
    cv_document_id: int,
    profile_repo: CandidateProfileRepository = Depends(get_profile_repository),
    skill_repo: CandidateSkillRepository = Depends(get_skill_repository),
):
    profile = profile_repo.find_by_cv_document_id(cv_document_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Candidate profile untuk cv_document_id={cv_document_id} tidak ditemukan."
        )

    # Ambil skills
    skills = skill_repo.find_by_candidate_profile_id(profile.id)  # type: ignore[arg-type]
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
    )


@router.get(
    "/",
    response_model=list[CandidateProfileResponse],
    summary="List semua candidate profile",
)
def list_candidate_profiles(
    limit: int = 20,
    offset: int = 0,
    profile_repo: CandidateProfileRepository = Depends(get_profile_repository),
):
    profiles = profile_repo.find_all(limit=limit, offset=offset)

    return [
        CandidateProfileResponse(
            id=p.id,
            uuid=p.uuid,
            cv_document_id=p.cv_document_id,
            full_name=p.full_name,
            email=p.email,
            phone_number=p.phone_number,
            current_location=p.current_location,
            parser_status=p.parser_status,
        )
        for p in profiles
    ]
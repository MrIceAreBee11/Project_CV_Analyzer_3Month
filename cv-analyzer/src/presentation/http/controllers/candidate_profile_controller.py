"""
Controller : CandidateProfileController
Layer      : Presentation > HTTP > Controllers
Phase      : 3 - Update — tambah repository baru di dependency injection
 
Endpoints:
    POST /candidate-profiles/build/{cv_document_id}
    GET  /candidate-profiles/by-document/{cv_document_id}
    GET  /candidate-profiles/
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.database import get_db
from src.app.dto.parser.candidate_profile_dto import (
    BuildCandidateProfileResponse,
    CandidateProfileResponse,
    CandidateSkillResponse,
    CandidateExperienceResponse,
    CandidateEducationResponse,
    CandidateCertificationResponse,

)
from src.app.use_cases.parser.build_candidate_profile import (
    BuildCandidateProfile
)

# Infrastructure — repositories
# Repositories Phase 1 & 2
from src.infrastructure.repositories.cv_document_repository import CvDocumentRepository
from src.infrastructure.repositories.cv_ocr_result_repository import CvOcrResultRepository
from src.infrastructure.repositories.candidate_profile_repository import CandidateProfileRepository
from src.infrastructure.repositories.candidate_skill_repository import CandidateSkillRepository
 
# Repositories Phase 3
from src.infrastructure.repositories.candidate_experience_repository import CandidateExperienceRepository
from src.infrastructure.repositories.candidate_education_repository import CandidateEducationRepository
from src.infrastructure.repositories.candidate_certification_repository import CandidateCertificationRepository

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
        candidate_experience_repository=CandidateExperienceRepository(db),
        candidate_education_repository=CandidateEducationRepository(db),
        candidate_certification_repository=CandidateCertificationRepository(db),
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

def get_experience_repository(
    db: Session = Depends(get_db)
) -> CandidateExperienceRepository:
    return CandidateExperienceRepository(db)

def get_education_repository(
    db: Session = Depends(get_db)
) -> CandidateEducationRepository:
    return CandidateEducationRepository(db)

def get_certification_repository(
    db: Session = Depends(get_db)
) -> CandidateCertificationRepository:
    return CandidateCertificationRepository(db)


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post(
    "/build/{cv_document_id}",
    response_model=BuildCandidateProfileResponse,
    summary="Build candidate profile dari hasil OCR",
    description=(
        "Trigger proses parsing raw OCR text menjadi candidate profile lengkap. "
        "CV Document harus sudah berstatus 'ocr_completed'."
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
    summary="Lihat candidate profile lengkap berdasarkan cv_document_id",
)

def get_profile_by_document(
    cv_document_id: int,
    profile_repo: CandidateProfileRepository = Depends(get_profile_repository),
    skill_repo: CandidateSkillRepository = Depends(get_skill_repository),
    experience_repo: CandidateExperienceRepository = Depends(get_experience_repository),
    education_repo: CandidateEducationRepository = Depends(get_education_repository),
    certification_repo: CandidateCertificationRepository = Depends(get_certification_repository),
):
    profile = profile_repo.find_by_cv_document_id(cv_document_id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Candidate profile untuk cv_document_id={cv_document_id} tidak ditemukan."
        )

    # Ambil skills
    if profile.id is None:
        raise HTTPException(
            status_code=500,
            detail="Candidate profile tidak memiliki ID. Data mungkin belum tersimpan dengan benar."
        )
    profile_id: int = profile.id  # type: ignore[arg-type]
 
    skills         = skill_repo.find_by_candidate_profile_id(profile_id)
    experiences    = experience_repo.find_by_candidate_profile_id(profile_id)
    educations     = education_repo.find_by_candidate_profile_id(profile_id)
    certifications = certification_repo.find_by_candidate_profile_id(profile_id)

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
        skills=[
            CandidateSkillResponse(
                id=s.id, skill_name=s.skill_name,
                skill_category=s.skill_category,
                source_section=s.source_section,
                confidence_score=s.confidence_score,
                is_primary=s.is_primary,
            )
            for s in skills
        ],
        experiences=[
            CandidateExperienceResponse(
                id=e.id, company_name=e.company_name,
                job_title=e.job_title,
                location_text=e.location_text,
                start_date_text=e.start_date_text,
                end_date_text=e.end_date_text,
                is_current=e.is_current, duration_text=e.duration_text,
                description_text=e.description_text, sort_order=e.sort_order,
            )
            for e in experiences
        ],
        educations=[
            CandidateEducationResponse(
                id=ed.id, institution_name=ed.institution_name,
                degree_name=ed.degree_name, major_name=ed.major_name,
                education_level=ed.education_level,
                start_date_text=ed.start_date_text,
                end_date_text=ed.end_date_text,
                gpa_text=ed.gpa_text,
                description_text=ed.description_text,
                sort_order=ed.sort_order,
            )
            for ed in educations
        ],
        certifications=[
            CandidateCertificationResponse(
                id=c.id, certification_name=c.certification_name,
                issuer_name=c.issuer_name,
                issue_date_text=c.issue_date_text,
                expiration_date_text=c.expiration_date_text,
                credential_id=c.credential_id,
                credential_url=c.credential_url,
            )
            for c in certifications
         ],
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

@router.get(
    "/debug-ocr/{cv_document_id}",
    summary="Debug : lihat raw ocr text",
    tags=["Debug"]
)
def debug_ocr_result(
    cv_document_id: int,
    db: Session = Depends(get_db),
):
    from src.infrastructure.repositories.cv_ocr_result_repository import (
        CvOcrResultRepository
    )
    ocr_repo    = CvOcrResultRepository(db)
    ocr_results = ocr_repo.find_by_cv_document_id(cv_document_id)

    if not ocr_results:
        return {"error": "Tidak ada OCR result"}

    ocr_results.sort(key=lambda x: x.page_number or 0)
    merged = "\n\n".join(
        r.raw_text for r in ocr_results
        if r.raw_text and r.raw_text.strip()
    )

    # Tampilkan baris per baris agar mudah dibaca
    lines = merged.splitlines()
    return {
        "total_lines": len(lines),
        "lines": [
            {"no": i + 1, "text": line}
            for i, line in enumerate(lines)
            if line.strip()  # skip baris kosong
        ]
    }
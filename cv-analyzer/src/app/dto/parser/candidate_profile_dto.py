"""
DTO     : CandidateProfileDTO
Layer   : App > DTO > Parser
Fungsi  : Struktur data request dan response untuk candidate profile.
          Digunakan di presentation layer (controller & routes).
Phase   : 2 - Basic Parser
Phase   : 3 - (Update) tambah experiences, educations, certifications 
"""

from pydantic import BaseModel
from typing import Optional, List


# ── Response: Satu Skill ───────────────────────────────────────────────────────

class CandidateSkillResponse(BaseModel):
    """Response struktur untuk satu skill kandidat."""
    id: Optional[int] = None
    skill_name: Optional[str] = None
    skill_category: Optional[str] = None
    source_section: Optional[str] = None
    confidence_score: Optional[float] = None
    is_primary: bool = False

    class Config:
        from_attributes = True

# ── Response: Experience ───────────────────────────────────────────────────────
 
class CandidateExperienceResponse(BaseModel):
    id: Optional[int] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    employment_type: Optional[str] = None
    location_text: Optional[str] = None
    start_date_text: Optional[str] = None
    end_date_text: Optional[str] = None
    is_current: bool = False
    duration_text: Optional[str] = None
    description_text: Optional[str] = None
    sort_order: int = 0
 
    class Config:
        from_attributes = True

# ── Response: Education ────────────────────────────────────────────────────────
 
class CandidateEducationResponse(BaseModel):
    id: Optional[int] = None
    institution_name: Optional[str] = None
    degree_name: Optional[str] = None
    major_name: Optional[str] = None
    education_level: Optional[str] = None
    start_date_text: Optional[str] = None
    end_date_text: Optional[str] = None
    gpa_text: Optional[str] = None
    description_text: Optional[str] = None
    sort_order: int = 0
 
    class Config:
        from_attributes = True

# ── Response: Certification ────────────────────────────────────────────────────
 
class CandidateCertificationResponse(BaseModel):
    id: Optional[int] = None
    certification_name: Optional[str] = None
    issuer_name: Optional[str] = None
    issue_date_text: Optional[str] = None
    expiration_date_text: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
 
    class Config:
        from_attributes = True

# ── Response: Candidate Profile ────────────────────────────────────────────────

class CandidateProfileResponse(BaseModel):
    """Response struktur lengkap untuk candidate profile."""
    id: Optional[int] = None
    uuid: Optional[str] = None
    cv_document_id: Optional[int] = None

    # Identitas
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    current_location: Optional[str] = None

    # Profesional
    professional_summary: Optional[str] = None
    latest_job_title: Optional[str] = None
    latest_company_name: Optional[str] = None

    # Social links
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    # Parser info
    parser_version: Optional[str] = None
    parser_status: Optional[str] = None
    parser_notes: Optional[str] = None

    # Structured data — Phase 3
    skills: List[CandidateSkillResponse] = []
    experiences: List[CandidateExperienceResponse] = []
    educations: List[CandidateEducationResponse] = []
    certifications: List[CandidateCertificationResponse] = []

    class Config:
        from_attributes = True

# ── Response: Build Result ─────────────────────────────────────────────────────

class BuildCandidateProfileResponse(BaseModel):
    """Response setelah proses build candidate profile selesai."""
    success: bool
    message: str
    profile: Optional[CandidateProfileResponse] = None
    total_skills_found: int = 0
    total_experiences_found: int = 0
    total_educations_found: int = 0
    total_certifications_found: int = 0
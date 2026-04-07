"""
Entity: CandidateEducation
Layer : Domain > Entities
Fungsi: Representasi satu riwayat pendidikan kandidat.
Phase : 3 - Structured Candidate Data
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class CandidateEducation:
    """Entitas untuk satu pendidikan kandidat."""
    id: Optional[int] = None
    candidate_profile_id: Optional[int] = None

    institution_name: Optional[str] = None
    degree_name: Optional[str] = None
    major_name: Optional[str] = None
    education_level: Optional[str] = None
    start_date_text: Optional[str] = None
    end_date_text: Optional[str] = None
    gpa_text: Optional[str] = None
    description_text: Optional[str] = None
    sort_order: int = 0

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_valid(self) -> bool:
        """Validasi sederhana untuk memastikan data pendidikan minimal memiliki institution_name dan degree_name."""
        return (
            self.institution_name is not None and self.institution_name.strip() != "" and
            self.degree_name is not None and self.degree_name.strip() != ""
        )
    def is_university(self) -> bool:
        """Cek apakah pendidikan ini adalah gelar universitas (S1, S2, S3)."""
        if self.education_level:
            return self.education_level.upper() in ["D3", "D4","S1", "S2", "S3", "BACHELOR", "MASTER", "PHD", "DOCTORATE"]
        return False
    
    def __repr__(self) -> str:
        return (
            f"<CandidateEducation "
            f"id={self.id} "
            f"institution='{self.institution_name}' "
            f"degree='{self.degree_name}'>"
        )
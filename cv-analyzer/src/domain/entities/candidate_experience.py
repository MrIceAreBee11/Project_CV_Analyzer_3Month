"""
Entity: CandidateExperience
Layer : Domain > Entities
Fungsi: Representasi satu riwayat pengalaman kerja kandidat.
Phase : 3 - Structured Candidate Data
 
Aturan domain:
- Tidak boleh import dari infrastructure atau framework apapun
- Field yang tidak ditemukan parser bernilai None
- is_current True jika kandidat masih bekerja di tempat ini
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class CandidateExperience:
    """Entitas untuk satu pengalaman kerja kandidat."""
    id: Optional[int] = None
    candidate_profile_id: Optional[int] = None

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

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_valid(self) -> bool:
        """Validasi sederhana untuk memastikan data pengalaman kerja minimal memiliki company_name dan job_title."""
        return (
            self.company_name is not None and self.company_name.strip() != "" and
            self.job_title is not None and self.job_title.strip() != ""
        )
    def is_internship(self) -> bool:
        """Cek apakah pengalaman kerja ini adalah magang/praktik."""
        if self.employment_type:
            return "intern" in self.employment_type.lower() or "magang" in self.employment_type.lower()
        return False
    def __repr__(self) -> str:
        return (
            f"<CandidateExperience "
            f"id={self.id} "
            f"title='{self.job_title}' "
            f"company='{self.company_name}'>"
        )
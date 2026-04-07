"""
Entity: CandidateCertification
Layer : Domain > Entities
Fungsi: Representasi satu sertifikasi kandidat.
Phase : 3 - Structured Candidate Data
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class CandidateCertification:

    """Entitas untuk satu sertifikasi kandidat."""
    id: Optional[int] = None
    candidate_profile_id: Optional[int] = None

    certification_name: Optional[str] = None
    issuer_name: Optional[str] = None
    issue_date_text: Optional[str] = None
    expiration_date_text: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    description_text: Optional[str] = None
    sort_order: int = 0

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def is_valid(self) -> bool:
        """Validasi sederhana untuk memastikan data sertifikasi minimal memiliki certification_name."""
        return (
            self.certification_name is not None and self.certification_name.strip() != ""
        )
    def has_credential(self) -> bool:
        """Cek apakah sertifikasi ini memiliki credential_id atau credential_url."""
        return (
            (self.credential_id is not None and self.credential_id.strip() != "") or
            (self.credential_url is not None and self.credential_url.strip() != "")
        )
    
    def __repr__(self) -> str:
        return (
            f"<CandidateCertification "
            f"id={self.id} "
            f"name='{self.certification_name}' "
            f"issuer='{self.issuer_name}'>"
        )
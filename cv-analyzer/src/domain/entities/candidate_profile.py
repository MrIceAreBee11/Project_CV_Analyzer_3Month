"""
Entity: CandidateProfile
Layer : Domain > Entities
Fungsi: Representasi objek kandidat yang sudah terstruktur
        hasil dari proses parsing raw OCR text.
Phase : 2 - Basic Parser

Aturan domain:
- Entity ini TIDAK boleh import dari infrastructure atau framework apapun
- Semua field yang tidak ditemukan parser bernilai None, bukan error
- parser_status merepresentasikan kondisi proses parsing
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from src.domain.entities.candidate_skill import CandidateSkill


@dataclass
class CandidateProfile:
    """
    Representasi data kandidat yang sudah terstruktur.
    Dihasilkan setelah proses parsing raw OCR text selesai.
    """

    # ── Primary Identity ───────────────────────────────────────────────────────
    id: Optional[int] = None
    uuid: Optional[str] = None

    # ── Relasi ke CV Document ──────────────────────────────────────────────────
    cv_document_id: Optional[int] = None

    # ── Identitas Kandidat ─────────────────────────────────────────────────────
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    alternate_phone_number: Optional[str] = None
    current_location: Optional[str] = None
    address_text: Optional[str] = None

    # ── Informasi Profesional ──────────────────────────────────────────────────
    professional_summary: Optional[str] = None
    date_of_birth_text: Optional[str] = None
    total_experience_text: Optional[str] = None
    estimated_total_experience_months: Optional[int] = None
    latest_job_title: Optional[str] = None
    latest_company_name: Optional[str] = None

    # ── Social Links ───────────────────────────────────────────────────────────
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    # ── Parser Metadata ────────────────────────────────────────────────────────
    raw_text: Optional[str] = None
    parser_version: str = "1.0.0"
    parser_status: str = "pending"
    parser_notes: Optional[str] = None

    # ── Timestamps ─────────────────────────────────────────────────────────────
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    # ── Relasi (diisi setelah fetch dari repository) ───────────────────────────
    skills: List[CandidateSkill] = field(default_factory=list)

    # ── Domain Methods ─────────────────────────────────────────────────────────
    def is_identity_complete(self) -> bool:
        """
        Cek apakah identitas dasar kandidat sudah lengkap.
        Minimal: nama, email, dan nomor telepon harus ada.
        """
        return all([
            self.full_name is not None,
            self.email is not None,
            self.phone_number is not None,
        ])

    def is_parsed(self) -> bool:
        """Cek apakah proses parsing sudah selesai."""
        return self.parser_status == "completed"

    def is_failed(self) -> bool:
        """Cek apakah proses parsing gagal."""
        return self.parser_status == "failed"

    def mark_as_completed(self) -> None:
        """Tandai parsing sebagai selesai."""
        self.parser_status = "completed"

    def mark_as_failed(self, reason: str) -> None:
        """Tandai parsing sebagai gagal dengan alasan."""
        self.parser_status = "failed"
        self.parser_notes = reason

    def get_skill_names(self) -> List[str]:
        """Ambil daftar nama skill kandidat."""
        return [
            skill.skill_name 
            for skill in self.skills
            if skill.skill_name is not None]

    def __repr__(self) -> str:
        return (
            f"<CandidateProfile "
            f"id={self.id} "
            f"name='{self.full_name}' "
            f"status='{self.parser_status}'>"
        )
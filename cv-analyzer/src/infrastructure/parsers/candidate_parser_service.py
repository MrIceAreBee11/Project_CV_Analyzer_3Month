"""
Service : CandidateParserService
Layer   : Infrastructure > Parsers
Fungsi  : Implementasi konkret dari ICandidateParserService.
          Menggabungkan IdentityParser dan SkillsParser menjadi
          satu service yang kohesif.
Phase   : 2 - Basic Parser

Catatan:
- Class ini mengimplementasikan interface ICandidateParserService
- Use case hanya mengenal interface-nya, bukan class ini langsung
- Mengikuti prinsip Dependency Inversion (SOLID)
"""

from sqlalchemy.orm import Session
from typing import List

from src.app.interfaces.services.i_candidate_parser_service import (
    ICandidateParserService
)
from src.domain.entities.candidate_profile import CandidateProfile
from src.domain.entities.candidate_skill import CandidateSkill
from src.infrastructure.parsers.regex.identity_parser import IdentityParser
from src.infrastructure.parsers.regex.skills_parser import SkillsParser


class CandidateParserService(ICandidateParserService):
    """
    Implementasi konkret parser kandidat berbasis regex.
    Menggunakan IdentityParser untuk identitas
    dan SkillsParser untuk skill extraction.
    """

    def __init__(self, db: Session):
        """
        Args:
            db: SQLAlchemy session, dibutuhkan oleh SkillsParser
                untuk membaca skill_dictionaries
        """
        self._identity_parser = IdentityParser()
        self._skills_parser   = SkillsParser(db=db)

    def extract_identity(self, raw_text: str) -> CandidateProfile:
        """
        Ekstrak identitas dasar kandidat dari raw text.

        Args:
            raw_text: teks mentah hasil OCR

        Returns:
            CandidateProfile berisi identitas yang berhasil diekstrak.
            Field tidak ditemukan bernilai None.
        """
        return self._identity_parser.extract(raw_text)

    def extract_skills(
        self,
        raw_text: str,
        candidate_profile_id: int
    ) -> List[CandidateSkill]:
        """
        Ekstrak daftar skill dari raw text.

        Args:
            raw_text             : teks mentah hasil OCR
            candidate_profile_id : ID candidate profile pemilik skill

        Returns:
            List CandidateSkill. List kosong jika tidak ada yang cocok.
        """
        return self._skills_parser.extract(
            raw_text=raw_text,
            candidate_profile_id=candidate_profile_id,
        )
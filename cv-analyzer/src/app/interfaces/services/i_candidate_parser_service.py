"""
Interface: ICandidateParserService
Layer    : App > Interfaces > Services
Fungsi   : Kontrak/abstraksi untuk proses parsing raw OCR text
           menjadi data kandidat yang terstruktur.
Phase    : 2 - Basic Parser

Prinsip SOLID yang diterapkan:
- O (Open/Closed): parser baru bisa ditambah tanpa ubah use case
- D (Dependency Inversion): use case bergantung pada abstraksi ini,
  bukan langsung ke implementasi regex atau NLP parser
"""

from abc import ABC, abstractmethod
from typing import List
from src.domain.entities.candidate_profile import CandidateProfile
from src.domain.entities.candidate_skill import CandidateSkill


class ICandidateParserService(ABC):
    """
    Kontrak service untuk parsing raw OCR text.
    Implementasi konkret ada di infrastructure/parsers/.
    """

    @abstractmethod
    def extract_identity(self, raw_text: str) -> CandidateProfile:
        """
        Ekstrak identitas dasar kandidat dari raw text.
        Meliputi: nama, email, phone, lokasi.

        Args:
            raw_text: teks mentah hasil OCR

        Returns:
            CandidateProfile berisi data identitas yang berhasil diekstrak.
            Field yang tidak ditemukan bernilai None (bukan error).
        """
        raise NotImplementedError

    @abstractmethod
    def extract_skills(
        self,
        raw_text: str,
        candidate_profile_id: int
    ) -> List[CandidateSkill]:
        """
        Ekstrak daftar skill dari raw text menggunakan skill dictionary.

        Args:
            raw_text           : teks mentah hasil OCR
            candidate_profile_id: ID candidate profile pemilik skill ini

        Returns:
            List CandidateSkill yang berhasil ditemukan.
            List kosong jika tidak ada skill yang cocok.
        """
        raise NotImplementedError
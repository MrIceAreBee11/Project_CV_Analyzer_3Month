"""
Interface: ICandidateProfileRepository
Layer    : App > Interfaces > Repositories
Fungsi   : Kontrak/abstraksi akses data untuk CandidateProfile.
           Use case hanya boleh bergantung pada interface ini,
           bukan pada implementasi konkret di infrastructure.
Phase    : 2 - Basic Parser

Prinsip SOLID yang diterapkan:
- D (Dependency Inversion): use case bergantung pada abstraksi ini
- I (Interface Segregation): interface ini hanya untuk candidate profile
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.candidate_profile import CandidateProfile


class ICandidateProfileRepository(ABC):
    """
    Kontrak repository untuk operasi data CandidateProfile.
    Semua implementasi konkret harus mengikuti interface ini.
    """

    @abstractmethod
    def save(self, candidate_profile: CandidateProfile) -> CandidateProfile:
        """
        Simpan candidate profile baru ke database.

        Args:
            candidate_profile: objek CandidateProfile yang akan disimpan

        Returns:
            CandidateProfile yang sudah tersimpan lengkap dengan id
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, candidate_profile: CandidateProfile) -> CandidateProfile:
        """
        Update candidate profile yang sudah ada di database.

        Args:
            candidate_profile: objek CandidateProfile dengan data terbaru

        Returns:
            CandidateProfile yang sudah diupdate
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, profile_id: int) -> Optional[CandidateProfile]:
        """
        Cari candidate profile berdasarkan ID.

        Args:
            profile_id: ID candidate profile

        Returns:
            CandidateProfile jika ditemukan, None jika tidak ada
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_uuid(self, uuid: str) -> Optional[CandidateProfile]:
        """
        Cari candidate profile berdasarkan UUID.

        Args:
            uuid: UUID candidate profile

        Returns:
            CandidateProfile jika ditemukan, None jika tidak ada
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_cv_document_id(
        self, cv_document_id: int
    ) -> Optional[CandidateProfile]:
        """
        Cari candidate profile berdasarkan cv_document_id.
        Relasi 1:1 — satu dokumen hanya punya satu profile.

        Args:
            cv_document_id: ID cv_document

        Returns:
            CandidateProfile jika ditemukan, None jika tidak ada
        """
        raise NotImplementedError

    @abstractmethod
    def find_all(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> List[CandidateProfile]:
        """
        Ambil semua candidate profile dengan pagination.

        Args:
            limit : jumlah data per halaman
            offset: posisi mulai data

        Returns:
            List CandidateProfile
        """
        raise NotImplementedError

    @abstractmethod
    def delete_by_id(self, profile_id: int) -> bool:
        """
        Hapus candidate profile berdasarkan ID (soft delete).

        Args:
            profile_id: ID candidate profile

        Returns:
            True jika berhasil dihapus, False jika tidak ditemukan
        """
        raise NotImplementedError
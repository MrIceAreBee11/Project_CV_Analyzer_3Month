"""
Interface: ICandidateSkillRepository
Layer    : App > Interfaces > Repositories
Fungsi   : Kontrak/abstraksi akses data untuk CandidateSkill.
Phase    : 2 - Basic Parser
"""

from abc import ABC, abstractmethod
from typing import List
from src.domain.entities.candidate_skill import CandidateSkill


class ICandidateSkillRepository(ABC):
    """
    Kontrak repository untuk operasi data CandidateSkill.
    """

    @abstractmethod
    def save_many(
        self,
        skills: List[CandidateSkill]
    ) -> List[CandidateSkill]:
        """
        Simpan banyak skill sekaligus (bulk insert).
        Lebih efisien daripada save satu per satu.

        Args:
            skills: list CandidateSkill yang akan disimpan

        Returns:
            List CandidateSkill yang sudah tersimpan
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_candidate_profile_id(
        self,
        candidate_profile_id: int
    ) -> List[CandidateSkill]:
        """
        Ambil semua skill milik satu candidate profile.

        Args:
            candidate_profile_id: ID candidate profile

        Returns:
            List CandidateSkill
        """
        raise NotImplementedError

    @abstractmethod
    def delete_by_candidate_profile_id(
        self,
        candidate_profile_id: int
    ) -> bool:
        """
        Hapus semua skill milik satu candidate profile.
        Dipakai saat reparse — skill lama dihapus, diganti skill baru.

        Args:
            candidate_profile_id: ID candidate profile

        Returns:
            True jika berhasil
        """
        raise NotImplementedError
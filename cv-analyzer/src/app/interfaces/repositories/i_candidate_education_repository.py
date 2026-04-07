"""
Interface: ICandidateEducationRepository
Layer    : App > Interfaces > Repositories
Phase    : 3 - Structured Candidate Data
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.candidate_education import CandidateEducation

class ICandidateEducationRepository(ABC):
    @abstractmethod
    def save_many(self, educations: List[CandidateEducation]) -> List[CandidateEducation]:
        """Simpan banyak entitas CandidateEducation sekaligus."""
        raise NotImplementedError
    
    @abstractmethod
    def find_by_candidate_profile_id(self, candidate_profile_id: int) -> List[CandidateEducation]:
        """Cari semua pendidikan berdasarkan candidate_profile_id."""
        raise NotImplementedError
    
    @abstractmethod
    def delete_by_candidate_profile_id(self, candidate_profile_id: int) -> bool:
        """Hapus semua pendidikan yang terkait dengan candidate_profile_id."""
        raise NotImplementedError
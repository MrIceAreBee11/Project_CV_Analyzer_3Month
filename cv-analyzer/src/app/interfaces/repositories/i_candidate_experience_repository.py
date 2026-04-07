"""
Interface: ICandidateExperienceRepository
Layer    : App > Interfaces > Repositories
Phase    : 3 - Structured Candidate Data
"""
 
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.candidate_experience import CandidateExperience

class ICandidateExperienceRepository(ABC):
    
    @abstractmethod
    def save_many(self, experiences: List[CandidateExperience]) -> List[CandidateExperience]:
        """Simpan banyak entitas CandidateExperience sekaligus."""
        raise NotImplementedError
    
    @abstractmethod
    def find_by_candidate_profile_id(self, candidate_profile_id: int) -> List[CandidateExperience]:
        """Cari semua pengalaman kerja berdasarkan candidate_profile_id."""
        raise NotImplementedError
    
    @abstractmethod
    def delete_by_candidate_profile_id(self, candidate_profile_id: int) -> bool:
        """Hapus semua pengalaman kerja yang terkait dengan candidate_profile_id."""
        raise NotImplementedError
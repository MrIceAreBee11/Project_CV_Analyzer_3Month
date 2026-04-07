"""
Interface: ICandidateCertificationRepository
Layer    : App > Interfaces > Repositories
Phase    : 3 - Structured Candidate Data
"""

from abc import ABC, abstractmethod
from typing import List, Optional  
from src.domain.entities.candidate_certification import CandidateCertification
class ICandidateCertificationRepository(ABC):
    
    @abstractmethod
    def save_many(self, certifications: List[CandidateCertification]) -> List[CandidateCertification]:
        """Simpan banyak entitas CandidateCertification sekaligus."""
        raise NotImplementedError
    
    @abstractmethod
    def find_by_candidate_profile_id(self, candidate_profile_id: int) -> List[CandidateCertification]:
        """Cari semua sertifikasi berdasarkan candidate_profile_id."""
        raise NotImplementedError
    
    @abstractmethod
    def delete_by_candidate_profile_id(self, candidate_profile_id: int) -> bool:
        """Hapus semua sertifikasi yang terkait dengan candidate_profile_id."""
        raise NotImplementedError
from abc import ABC, abstractmethod
from src.domain.entities.cv_document import CvDocument

class ICvDocumentRepository(ABC):

    @abstractmethod
    def save(self, cv_document: CvDocument) -> CvDocument:
        pass

    @abstractmethod
    def find_by_uuid(self, uuid: str) -> CvDocument | None:
        pass
    
    @abstractmethod
    def find_by_id(self, cv_document_id: int) -> CvDocument | None:
        """Cari CvDocument berdasarkan primary key ID."""
        pass
    @abstractmethod
    def update(self, cv_document: CvDocument) -> CvDocument:
        pass
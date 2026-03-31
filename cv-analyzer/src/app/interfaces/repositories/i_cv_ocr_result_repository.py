from abc import ABC, abstractmethod
from src.domain.entities.cv_ocr_result import CvOcrResult

class ICvOcrResultRepository(ABC):

    @abstractmethod
    def save(self, ocr_result: CvOcrResult) -> CvOcrResult:
        pass

    @abstractmethod
    def find_by_document_id(self, cv_document_id: int) -> list[CvOcrResult]:
        pass
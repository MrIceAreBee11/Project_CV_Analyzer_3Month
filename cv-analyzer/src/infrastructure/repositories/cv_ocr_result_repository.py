from sqlalchemy.orm import Session
from src.domain.entities.cv_ocr_result import CvOcrResult
from src.app.interfaces.repositories.i_cv_ocr_result_repository import ICvOcrResultRepository

class CvOcrResultRepository(ICvOcrResultRepository):

    def __init__(self, db: Session):
        self.db = db

    def save(self, ocr_result: CvOcrResult) -> CvOcrResult:
        self.db.add(ocr_result)
        self.db.commit()
        self.db.refresh(ocr_result)
        return ocr_result

    def find_by_document_id(self, cv_document_id: int) -> list[CvOcrResult]:
        return self.db.query(CvOcrResult).filter(
            CvOcrResult.cv_document_id == cv_document_id
        ).order_by(CvOcrResult.page_number).all()
    
    def find_by_cv_document_id(self, cv_document_id: int) -> list[CvOcrResult]:
        return self.find_by_document_id(cv_document_id)
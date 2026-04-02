from sqlalchemy.orm import Session
from src.domain.entities.cv_document import CvDocument
from src.app.interfaces.repositories.i_cv_document_repository import ICvDocumentRepository

class CvDocumentRepository(ICvDocumentRepository):

    def __init__(self, db: Session):
        self.db = db

    def save(self, cv_document: CvDocument) -> CvDocument:
        self.db.add(cv_document)
        self.db.commit()
        self.db.refresh(cv_document)
        return cv_document

    def find_by_uuid(self, uuid: str) -> CvDocument | None:
        return self.db.query(CvDocument).filter(
            CvDocument.uuid == uuid,
            CvDocument.deleted_at == None
        ).first()
    
    def find_by_id(self, document_id: int):
        """Cari cv_document berdasarkan ID."""
        return self.db.query(CvDocument).filter(
            CvDocument.id == document_id
        ).first()

    def update(self, cv_document):
        """Update status cv_document."""
        model = self.db.query(CvDocument).filter(
            CvDocument.id == cv_document.id
        ).first()

        if not model:
            raise ValueError(f"CvDocument id={cv_document.id} tidak ditemukan")

        model.status = cv_document.status
        self.db.commit()
        self.db.refresh(model)
        return model
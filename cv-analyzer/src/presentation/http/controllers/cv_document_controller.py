from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from config.database import get_db
from src.app.use_cases.cv_document.create_cv_upload import CreateCvUploadUseCase
from src.app.use_cases.cv_document.process_cv_ocr import ProcessCvOcrUseCase
from src.infrastructure.repositories.cv_document_repository import CvDocumentRepository
from src.infrastructure.repositories.cv_ocr_result_repository import CvOcrResultRepository
from src.app.dto.cv_document.cv_document_dto import CvDocumentUploadResponse

router = APIRouter()

@router.post("/upload", response_model=CvDocumentUploadResponse)
def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    repository = CvDocumentRepository(db)
    use_case = CreateCvUploadUseCase(repository)
    result = use_case.execute(file)
    return result


@router.post("/{uuid}/ocr")
def process_ocr(
    uuid: str,
    db: Session = Depends(get_db)
):
    cv_repo = CvDocumentRepository(db)
    ocr_repo = CvOcrResultRepository(db)
    use_case = ProcessCvOcrUseCase(cv_repo, ocr_repo)
    result = use_case.execute(uuid)
    return result
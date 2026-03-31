import uuid
import os
import shutil
from datetime import datetime
from fastapi import UploadFile, HTTPException
from src.domain.entities.cv_document import CvDocument
from src.app.interfaces.repositories.i_cv_document_repository import ICvDocumentRepository
from config.settings import settings

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png"
}

class CreateCvUploadUseCase:

    def __init__(self, repository: ICvDocumentRepository):
        self.repository = repository

    def execute(self, file: UploadFile, uploaded_by: str = "system") -> CvDocument:

        # 1. Validasi filename
        if not file.filename:
            raise HTTPException(
                status_code=422,
                detail= "Nama File tidak valid"
            )
        
        # 2. Validasi extension
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=422,
                detail="Format file tidak didukung. Gunakan: PDF, JPG, JPEG, PNG"
            )

        # 3. Validasi mime type
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=422,
                detail=f"Tipe file tidak valid."
            )

        # 4. Baca file & validasi ukuran
        file_bytes = file.file.read()
        file_size = len(file_bytes)
        max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024

        if file_size > max_size:
            raise HTTPException(
                status_code=422,
                detail=f"Ukuran file melebihi batas {settings.MAX_FILE_SIZE_MB}MB"
            )

        # 5. Generate UUID & nama file unik
        file_uuid = str(uuid.uuid4())
        unique_file_name = f"{file_uuid}.{file_extension}"

        # 6. Simpan file ke folder uploads/
        upload_dir = settings.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)
        storage_path = os.path.join(upload_dir, unique_file_name)

        with open(storage_path, "wb") as f:
            f.write(file_bytes)

        # 7. Buat record cv_document
        now = datetime.utcnow()
        cv_document = CvDocument(
            uuid=file_uuid,
            file_name=unique_file_name,
            original_file_name=file.filename,
            file_extension=file_extension,
            mime_type=file.content_type,
            file_size=file_size,
            storage_path=storage_path,
            uploaded_by=uploaded_by,
            upload_source="api",
            status="uploaded",
            uploaded_at=now,
            created_at=now,
            updated_at=now
        )

        # 8. Simpan ke database
        return self.repository.save(cv_document)
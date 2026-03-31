import json
import time
from datetime import datetime
from fastapi import HTTPException
from paddleocr import PaddleOCR
from src.domain.entities.cv_document import CvDocument
from src.domain.entities.cv_ocr_result import CvOcrResult
from src.app.interfaces.repositories.i_cv_document_repository import ICvDocumentRepository
from src.app.interfaces.repositories.i_cv_ocr_result_repository import ICvOcrResultRepository

# Inisialisasi PaddleOCR sekali saja
ocr_engine = PaddleOCR(use_angle_cls=True, lang="en")

class ProcessCvOcrUseCase:

    def __init__(
        self,
        cv_document_repository: ICvDocumentRepository,
        ocr_result_repository: ICvOcrResultRepository
    ):
        self.cv_document_repository = cv_document_repository
        self.ocr_result_repository = ocr_result_repository

    def execute(self, document_uuid: str) -> dict:

        # 1. Cari dokumen berdasarkan UUID
        cv_document = self.cv_document_repository.find_by_uuid(document_uuid)
        if not cv_document:
            raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")
        assert isinstance(cv_document, CvDocument)
        # 2. Cek status dokumen
        if cv_document.status not in ["uploaded", "ocr_failed"]:
            raise HTTPException(
                status_code=422,
                detail=f"Dokumen tidak bisa diproses, status saat ini: {cv_document.status}"
            )

        # 3. Update status jadi processing
        cv_document.status = "processing_ocr"
        cv_document.ocr_started_at = datetime.utcnow()
        cv_document.updated_at = datetime.utcnow()
        self.cv_document_repository.save(cv_document)

        try:
            # 4. Jalankan OCR
            start_time = time.time()
            ocr_output = ocr_engine.ocr(cv_document.storage_path, cls=True)
            duration_ms = int((time.time() - start_time) * 1000)

            # 5. Proses hasil OCR
            raw_lines = []
            confidence_scores = []

            if ocr_output and ocr_output[0]:
                for line in ocr_output[0]:
                    text = line[1][0]        # teks hasil OCR
                    confidence = line[1][1]  # confidence score
                    raw_lines.append(text)
                    confidence_scores.append(confidence)

            # 6. Gabungkan semua teks
            raw_text = "\n".join(raw_lines)
            confidence_avg = (
                sum(confidence_scores) / len(confidence_scores)
                if confidence_scores else 0.0
            )

            # 7. Simpan hasil OCR ke database
            ocr_result = CvOcrResult(
                cv_document_id=cv_document.id,
                page_number=1,
                raw_text=raw_text,
                raw_json_result=json.dumps(ocr_output),
                confidence_average=round(confidence_avg, 4),
                processing_duration_ms=duration_ms,
                status="completed",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.ocr_result_repository.save(ocr_result)

            # 8. Update status dokumen jadi ocr_completed
            cv_document.status = "ocr_completed"
            cv_document.ocr_completed_at = datetime.utcnow()
            cv_document.updated_at = datetime.utcnow()
            self.cv_document_repository.save(cv_document)

            return {
                "uuid": document_uuid,
                "status": "ocr_completed",
                "total_lines": len(raw_lines),
                "confidence_average": round(confidence_avg, 4),
                "processing_duration_ms": duration_ms,
                "raw_text_preview": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text
            }

        except Exception as e:
            # 9. Kalau gagal, update status jadi ocr_failed
            cv_document.status = "ocr_failed"
            cv_document.error_message = str(e)
            cv_document.updated_at = datetime.utcnow()
            self.cv_document_repository.save(cv_document)

            raise HTTPException(
                status_code=500,
                detail=f"OCR gagal: {str(e)}"
            )
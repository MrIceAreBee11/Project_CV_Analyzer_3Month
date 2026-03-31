from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CvDocumentUploadResponse(BaseModel):
    uuid: str
    file_name: str
    original_file_name: str
    file_extension: str
    mime_type: str
    file_size: int
    status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True
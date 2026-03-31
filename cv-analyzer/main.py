from fastapi import FastAPI
from config.settings import settings
from src.presentation.http.controllers.cv_document_controller import router as cv_document_router

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)

app.include_router(
    cv_document_router,
    prefix="/api/cv-documents",
    tags=["CV Documents"]
)

@app.get("/")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
from fastapi import FastAPI
from config.settings import settings
from src.presentation.http.controllers.cv_document_controller import router as cv_document_router
from src.presentation.http.controllers.candidate_profile_controller import router as candidate_profile_router

app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0"
)

app.include_router(
    cv_document_router,
    prefix="/api/cv-documents",
    tags=["CV Documents"]
)

app.include_router(
    candidate_profile_router,
    prefix="/api/candidate-profiles",
    tags=["Candidate Profiles"]
)

@app.get("/")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
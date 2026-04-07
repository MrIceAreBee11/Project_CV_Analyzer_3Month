# Update Sementara - CV Analyzer Project

**Tanggal:** April 7, 2026  
**Versi Aplikasi:** 2.0.0  
**Status:** Development/In Progress

## 📋 Ringkasan Proyek

CV Analyzer adalah sistem berbasis FastAPI untuk menganalisis dokumen CV/resume menggunakan teknologi OCR (PaddleOCR). Sistem ini mengubah dokumen PDF atau gambar menjadi data terstruktur yang dapat digunakan untuk screening kandidat, pencarian, dan analisis HR.

## 🏗️ Arsitektur Sistem

### Teknologi Utama
- **Framework:** FastAPI 2.0.0
- **Database:** MySQL dengan SQLAlchemy
- **OCR Engine:** PaddleOCR
- **Bahasa:** Python
- **Arsitektur:** Domain-Driven Design (DDD)

### Struktur Proyek
```
cv-analyzer/
├── main.py                 # Entry point FastAPI
├── config/                 # Konfigurasi aplikasi
├── src/
│   ├── domain/            # Business logic entities
│   ├── app/               # Use cases, DTOs, interfaces
│   └── infrastructure/    # Parsers, repositories, providers
├── uploads/               # Direktori upload file
└── alembic/               # Database migrations
```

## ✅ Fitur yang Sudah Diimplementasi

### 1. Upload & Storage CV
- ✅ Upload file PDF/JPG/JPEG/PNG
- ✅ Validasi format dan ukuran file (max 10MB)
- ✅ Penyimpanan file dengan UUID
- ✅ Tracking status upload

### 2. Database Schema
- ✅ Tabel `cv_documents` - metadata dokumen
- ✅ Tabel `cv_ocr_results` - hasil OCR per halaman
- ✅ Tabel kandidat terstruktur:
  - `candidate_profiles` - profil utama kandidat
  - `candidate_experiences` - pengalaman kerja
  - `candidate_educations` - pendidikan
  - `candidate_skills` - keterampilan
  - `candidate_certifications` - sertifikasi

### 3. Pipeline Processing
Status pipeline yang didukung:
- `uploaded` → `queued_for_ocr` → `processing_ocr` → `ocr_completed` → `queued_for_parsing` → `parsing_completed` → `analyzed`

### 4. API Endpoints
- ✅ `GET /` - Health check
- ✅ `/api/cv-documents/*` - CRUD operations untuk CV documents
- ✅ `/api/candidate-profiles/*` - CRUD operations untuk candidate profiles

### 5. Domain Entities
- ✅ `CvDocument` - representasi dokumen CV
- ✅ `CandidateProfile` - data terstruktur kandidat
- ✅ Entities pendukung (Experience, Education, Skills, Certifications)

## 🚧 Dalam Pengembangan

### 1. OCR Processing
- 🔄 Integrasi PaddleOCR untuk ekstraksi teks
- 🔄 Pemrosesan multi-halaman PDF
- 🔄 Error handling untuk OCR failures

### 2. Text Parsing
- 🔄 Regex parsers untuk berbagai section CV:
  - Identity parser (nama, email, telepon)
  - Experience parser (pengalaman kerja)
  - Education parser (pendidikan)
  - Skills parser (keterampilan)
  - Certification parser (sertifikasi)

### 3. Use Cases
- 🔄 `ProcessCvOcr` - use case untuk OCR processing
- 🔄 `BuildCandidateProfile` - use case untuk parsing ke structured data

### 4. Infrastructure
- 🔄 Repository implementations
- 🔄 Service implementations
- 🔄 OCR provider integration

## ⚙️ Konfigurasi

### Environment Variables
```env
APP_NAME=CV Analyzer
APP_ENV=development
APP_PORT=8000

DB_HOST=localhost
DB_PORT=3306
DB_NAME=cv_analyzer
DB_USER=root
DB_PASSWORD=

UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=10
```

### Dependencies
**Catatan:** File `requirements.txt` perlu di-generate dengan `pip freeze > requirements.txt` setelah instalasi dependencies.

## 🗄️ Database Migrations

Menggunakan Alembic untuk migrasi database. Versi migrasi yang ada:
- `5b1d161f4d6c` - Create cv_ocr_results table
- `a1b2c3d4e5f6` - Create structured data tables
- `c92dada7449b` - Create cv_documents table
- `f7e8d9c0b1a2` - Create parser tables

## 🎯 Next Steps

### Prioritas Tinggi
1. **Setup OCR Pipeline** - Integrasi PaddleOCR
2. **Implement Parsers** - Regex parsers untuk ekstraksi data
3. **Complete Use Cases** - ProcessCvOcr dan BuildCandidateProfile
4. **API Testing** - Test semua endpoints

### Prioritas Menengah
1. **Error Handling** - Comprehensive error handling
2. **Logging** - Structured logging
3. **Validation** - Input validation untuk semua DTOs
4. **Documentation** - API documentation dengan Swagger

### Prioritas Rendah
1. **Authentication** - User authentication & authorization
2. **File Management** - Cleanup, archiving
3. **Performance** - Optimization untuk large files
4. **Monitoring** - Health checks, metrics

## 🔧 Setup & Installation

1. **Clone repository**
2. **Setup virtual environment**
3. **Install dependencies** (generate requirements.txt)
4. **Setup MySQL database**
5. **Configure environment variables**
6. **Run migrations**: `alembic upgrade head`
7. **Start server**: `uvicorn main:app --reload`

## 📝 Catatan Pengembangan

- Proyek menggunakan Domain-Driven Design principles
- Semua domain entities tidak boleh import dari infrastructure/framework
- Error handling menggunakan HTTPException untuk API responses
- File storage menggunakan UUID untuk unique naming
- Pipeline processing menggunakan status-based workflow

---

**Update berikutnya akan mencakup progress implementasi OCR dan parsing functionality.**
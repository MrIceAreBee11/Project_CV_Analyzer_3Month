# Project_CV_Analyzer_3Month
CV Analyzer OCR adalah sistem untuk membaca dokumen CV atau resume dalam format PDF atau image, mengekstrak teks menggunakan PaddleOCR, lalu memproses teks tersebut menjadi data terstruktur yang dapat digunakan untuk screening kandidat, pencarian kandidat, dashboard HR, dan proses analisis lanjutan.


## Setup

1. Clone repository ini
2. Copy file env: `cp .env.example .env`
3. Isi `.env` sesuai konfigurasi lokal kamu
4. Install dependencies: `pip install -r requirements.txt`
5. Jalankan migration: `alembic upgrade head`
6. Jalankan server: `python -m uvicorn main:app --reload --port 8000`

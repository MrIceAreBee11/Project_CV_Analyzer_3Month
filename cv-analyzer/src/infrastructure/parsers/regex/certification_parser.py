"""
Service : CertificationParser
Layer   : Infrastructure > Parsers > Regex
Fungsi  : Mengekstrak riwayat sertifikasi dari raw OCR text.
Phase   : 3 - Structured Candidate Data

Mendukung berbagai format CV:
    Format A: Nama | Issuer | Tanggal
        "AWS Certified Developer | Amazon | 2023"

    Format B: Nama – Issuer, Tanggal
        "Google Analytics Certification – Google, January 2023"

    Format C: Format Indonesia
        "Soft Skill Career Class: Student Employability Journey
         | Direktorat Karir, Alumni & Endowment (CAE)
         | February 23 - June 23, 2024"

    Format D: Bullet point sederhana
        "• Sertifikasi Python Programming – Dicoding, 2022"

    Format E: Training/Seminar tanpa issuer
        "Seminar Nasional Teknologi Informasi 2023"
"""

import re
from typing import List, Optional, Tuple
from src.domain.entities.candidate_certification import CandidateCertification


class CertificationParser:

    # ── Section Headers ────────────────────────────────────────────────────────
    CERTIFICATION_SECTION_PATTERN = re.compile(
        r"^(?:"
        r"certifications?|sertifikasi|sertifikat"
        r"|training(?:\s+and\s+seminar)?|seminar(?:\s+dan\s+pelatihan)?"
        r"|pelatihan|kursus|course[s]?"
        r"|licenses?\s+(?:and|&)\s+certifications?"
        r")$",
        re.IGNORECASE
    )

    # ── Section Enders ─────────────────────────────────────────────────────────
    END_SECTION_PATTERN = re.compile(
        r"^(?:"
        r"(?:technical\s+)?skills?|keahlian|kompetensi"
        r"|hard\s+skill|soft\s+skill|technical\s+and\s+non"
        r"|pendidikan|education"
        r"|(?:work\s+)?experience|pengalaman(?:\s+kerja)?"
        r"|organisasi|organizational|referensi|references?"
        r"|project\s+experience"
        r")$",
        re.IGNORECASE
    )

    # ── Date Patterns ──────────────────────────────────────────────────────────
    MONTH_NAMES = (
        r"januari|februari|maret|april|mei|juni|juli|agustus|september"
        r"|oktober|november|desember"
        r"|january|february|march|april|may|june|july|august|september"
        r"|october|november|december"
        r"|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec"
    )

    DATE_PATTERN = re.compile(
        r"(?:"
        # "February 23 - June 23, 2024" atau "Jan 2023 - Dec 2023"
        r"(?:(?:" + MONTH_NAMES + r")\s+\d{1,2}[\s,]*){1,2}\d{4}"
        r"|(?:" + MONTH_NAMES + r")\s+\d{4}"  # "January 2023"
        r"|\d{4}"                               # "2023"
        r")",
        re.IGNORECASE
    )

    # Separator yang umum digunakan antara komponen sertifikasi
    SEPARATOR_PATTERN = re.compile(r"\s*[|–\-—]\s*")

    # Bullet point markers
    BULLET_PATTERN = re.compile(r"^[•\-\*✓√►▸]\s*")

    # ── Public Methods ─────────────────────────────────────────────────────────

    def extract(
        self,
        raw_text: str,
        candidate_profile_id: int
    ) -> List[CandidateCertification]:
        if not raw_text or not raw_text.strip():
            return []

        lines        = raw_text.splitlines()
        cert_entries = self._extract_certification_entries(lines)

        certifications = []
        for entry in cert_entries:
            cert = self._parse_entry(entry, candidate_profile_id)
            if cert and cert.is_valid():
                certifications.append(cert)

        return certifications

    # ── Private: Entry Extraction ──────────────────────────────────────────────

    def _extract_certification_entries(
        self, lines: List[str]
    ) -> List[str]:
        """
        Kumpulkan semua entri sertifikasi dari section yang relevan.
        Multi-baris yang berkelanjutan digabung menjadi satu entri.
        """
        entries: List[str]       = []
        current_entry: List[str] = []
        in_section               = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                # Baris kosong → simpan entri sebelumnya jika ada
                if current_entry and in_section:
                    entries.append(" ".join(current_entry))
                    current_entry = []
                continue

            # Masuk section sertifikasi
            if self.CERTIFICATION_SECTION_PATTERN.match(stripped):
                in_section = True
                continue

            if not in_section:
                continue

            # Keluar section
            if self.END_SECTION_PATTERN.match(stripped):
                in_section = False
                if current_entry:
                    entries.append(" ".join(current_entry))
                    current_entry = []
                continue

            # Bersihkan bullet point
            cleaned = self.BULLET_PATTERN.sub("", stripped).strip()
            if not cleaned or len(cleaned) < 3:
                continue

            # Cek apakah ini awal entri baru:
            # - Diawali bullet point
            # - Atau ada | separator (biasanya awal entri baru)
            # - Atau entri sebelumnya sudah punya tanggal (lengkap)
            is_new_entry = (
                bool(self.BULLET_PATTERN.match(stripped))
                or (current_entry and self._entry_seems_complete(
                    " ".join(current_entry)
                ))
            )

            if is_new_entry and current_entry:
                entries.append(" ".join(current_entry))
                current_entry = []

            current_entry.append(cleaned)

        # Simpan entri terakhir
        if current_entry:
            entries.append(" ".join(current_entry))

        return entries

    def _entry_seems_complete(self, entry: str) -> bool:
        """
        Cek apakah entri sudah lengkap (punya nama + tanggal/issuer).
        Digunakan untuk menentukan apakah baris berikutnya adalah entri baru.
        """
        has_date    = bool(self.DATE_PATTERN.search(entry))
        has_separator = bool(self.SEPARATOR_PATTERN.search(entry))
        return has_date or has_separator

    # ── Private: Entry Parsing ─────────────────────────────────────────────────

    def _parse_entry(
        self,
        entry: str,
        candidate_profile_id: int
    ) -> Optional[CandidateCertification]:
        """
        Parse satu entri string menjadi CandidateCertification.

        Strategi:
        1. Ekstrak tanggal dari entri
        2. Pisahkan sisa teks dengan separator (|, –, -)
        3. Bagian pertama → certification_name
        4. Bagian berikutnya → issuer_name
        """
        if not entry or len(entry.strip()) < 3:
            return None

        cert = CandidateCertification(
            candidate_profile_id=candidate_profile_id
        )

        # Ekstrak semua tanggal yang ditemukan
        dates_found = self.DATE_PATTERN.findall(entry)
        if dates_found:
            # Tanggal pertama = issue date, terakhir = expiration (jika ada)
            cert.issue_date_text = dates_found[0].strip()
            if len(dates_found) > 1:
                cert.expiration_date_text = dates_found[-1].strip()

        # Hapus tanggal dari entry untuk parsing lebih bersih
        entry_no_date = self.DATE_PATTERN.sub("", entry).strip()
        entry_no_date = re.sub(r"\s{2,}", " ", entry_no_date).strip()

        # Pisahkan berdasarkan separator
        parts = self.SEPARATOR_PATTERN.split(entry_no_date)
        parts = [p.strip() for p in parts if p.strip()]

        if len(parts) >= 1:
            cert.certification_name = self._clean_name(parts[0])
        if len(parts) >= 2:
            cert.issuer_name = self._clean_name(parts[1])
        if len(parts) >= 3 and not cert.issue_date_text:
            # Bagian ketiga mungkin tanggal yang belum terekstrak
            cert.issue_date_text = parts[2]

        return cert

    # ── Private: Helpers ───────────────────────────────────────────────────────

    def _clean_name(self, text: str) -> Optional[str]:
        """Bersihkan nama dari karakter sisa separator atau spasi berlebih."""
        cleaned = re.sub(r"^[:\s]+|[:\s]+$", "", text).strip()
        cleaned = re.sub(r"\s{2,}", " ", cleaned)
        return cleaned if cleaned else None
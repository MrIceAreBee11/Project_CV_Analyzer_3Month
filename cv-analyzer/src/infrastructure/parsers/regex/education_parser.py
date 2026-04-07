"""
Service : EducationParser
Layer   : Infrastructure > Parsers > Regex
Fungsi  : Mengekstrak riwayat pendidikan dari raw OCR text.
Phase   : 3 - Structured Candidate Data

Mendukung berbagai format CV:
    Format A: Tahun dengan dash/pipe
        "Informatics Engineering"
        "Telkom University, Bandung - GPA 3.44/04.00 – 2021|2025"

    Format B: Tahun di awal baris
        "2019 – 2022  Universitas Indonesia"
        "Teknik Informatika"

    Format C: Tahun di akhir baris
        "Universitas Gadjah Mada | 2018 - 2022"
        "Ilmu Komputer, GPA 3.8"

    Format D: Format internasional
        "Bachelor of Computer Science"
        "Massachusetts Institute of Technology | 2018 - 2022"

    Format E: SMA/SMK format Indonesia
        "SMAN 1 Cisaat, Sukabumi – Scores 90.08 – 2018|2021"
"""

import re
from typing import List, Optional, Tuple
from src.domain.entities.candidate_education import CandidateEducation


class EducationParser:

    # ── Section Headers ────────────────────────────────────────────────────────
    EDUCATION_SECTION_PATTERN = re.compile(
        r"^(?:riwayat\s+)?pendidikan$|^education$|^academic\s+background$",
        re.IGNORECASE
    )

    # ── Section Enders ─────────────────────────────────────────────────────────
    END_SECTION_PATTERN = re.compile(
        r"^(?:"
        r"(?:technical\s+)?skills?|keahlian|kompetensi"
        r"|hard\s+skill|soft\s+skill|technical\s+and\s+non"
        r"|(?:work\s+)?experience|pengalaman(?:\s+kerja)?"
        r"|sertifikasi|certifications?|training|seminar|pelatihan"
        r"|organisasi|organizational|referensi|references?"
        r"|project\s+experience"
        r")$",
        re.IGNORECASE
    )

    # ── Year Range Patterns ────────────────────────────────────────────────────
    # Support: 2021-2025, 2021|2025, 2021/2025, 2021 – 2025
    YEAR_RANGE_PATTERN = re.compile(
        r"(?P<start>\d{4})\s*[–\-—|/]\s*(?P<end>\d{4}|sekarang|present|current|now)",
        re.IGNORECASE
    )

    # ── GPA Pattern ────────────────────────────────────────────────────────────
    GPA_PATTERN = re.compile(
        r"(?:gpa|ipk|nilai|score[s]?)\s*[:\-]?\s*(\d+[.,]\d+)"
        r"|(\d+[.,]\d+)\s*/\s*(?:4\.?0+|100)",
        re.IGNORECASE
    )

    # ── Education Level Keywords ───────────────────────────────────────────────
    EDUCATION_LEVEL_PATTERNS = [
        ("S3",  re.compile(r"\bS3\b|doktor|doctorate|ph\.?d", re.IGNORECASE)),
        ("S2",  re.compile(r"\bS2\b|magister|master(?:\s+of)?", re.IGNORECASE)),
        ("S1",  re.compile(r"\bS1\b|sarjana|bachelor(?:\s+of)?", re.IGNORECASE)),
        ("D4",  re.compile(r"\bD[-\s]?4\b|diploma\s*iv", re.IGNORECASE)),
        ("D3",  re.compile(r"\bD[-\s]?3\b|diploma\s*iii", re.IGNORECASE)),
        ("D2",  re.compile(r"\bD[-\s]?2\b|diploma\s*ii", re.IGNORECASE)),
        ("D1",  re.compile(r"\bD[-\s]?1\b|diploma\s*i", re.IGNORECASE)),
        ("SMA", re.compile(r"\bSMA[N]?\b|\bSMK[N]?\b|\bMA\b|senior\s+high", re.IGNORECASE)),
        ("SMP", re.compile(r"\bSMP[N]?\b|\bMTs\b|junior\s+high", re.IGNORECASE)),
        ("SD",  re.compile(r"\bSD[N]?\b|elementary|primary\s+school", re.IGNORECASE)),
    ]

    # ── Institution Keywords ───────────────────────────────────────────────────
    INSTITUTION_PATTERN = re.compile(
        r"\b(?:"
        r"universitas|university|institut(?:e)?|sekolah|college"
        r"|politeknik|polytechnic|akademi|academy"
        r"|SMA[N]?|SMK[N]?|SMP[N]?|SD[N]?|MTs|MA\b"
        r"|telkom|binus|ui\b|ugm|itb|ipb|unpad|undip|unair"
        r")\b",
        re.IGNORECASE
    )

    # ── Degree/Major Keywords ──────────────────────────────────────────────────
    DEGREE_PATTERN = re.compile(
        r"\b(?:"
        r"jurusan|program\s+studi|prodi|fakultas|department|major"
        r"|teknik\s+informatika|informatika|ilmu\s+komputer|computer\s+science"
        r"|sistem\s+informasi|information\s+system"
        r"|manajemen|management|akuntansi|accounting"
        r"|tata\s+busana|kelas\s+karyawan"
        r"|informatics\s+engineering|electrical\s+engineering"
        r"|science\s+major|ipa|ips"
        r")\b",
        re.IGNORECASE
    )

    # ── Public Methods ─────────────────────────────────────────────────────────

    def extract(
        self,
        raw_text: str,
        candidate_profile_id: int
    ) -> List[CandidateEducation]:
        if not raw_text or not raw_text.strip():
            return []

        lines  = raw_text.splitlines()
        blocks = self._extract_education_blocks(lines)

        educations = []
        for sort_idx, block in enumerate(blocks):
            edu = self._parse_block(block, candidate_profile_id, sort_idx)
            if edu and edu.is_valid():
                educations.append(edu)

        return educations

    # ── Private: Block Extraction ──────────────────────────────────────────────

    def _extract_education_blocks(
        self, lines: List[str]
    ) -> List[List[str]]:
        """
        Kumpulkan baris-baris dalam section pendidikan.
        Blok baru dimulai setiap ada nama institusi atau tahun range.
        """
        blocks: List[List[str]]  = []
        current_block: List[str] = []
        in_education_section     = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Masuk section education
            if self.EDUCATION_SECTION_PATTERN.match(stripped):
                in_education_section = True
                continue

            if not in_education_section:
                continue

            # Keluar section education
            if self.END_SECTION_PATTERN.match(stripped):
                in_education_section = False
                if current_block:
                    blocks.append(current_block)
                    current_block = []
                continue

            # Mulai blok baru jika:
            # 1. Ada nama institusi yang dikenali
            # 2. Ada bullet point (•) — biasanya awal entri baru
            is_institution = bool(self.INSTITUTION_PATTERN.search(stripped))
            is_bullet_institution = stripped.startswith("•") and \
                bool(self.INSTITUTION_PATTERN.search(stripped))

            if (is_institution or is_bullet_institution) and current_block:
                # Cek apakah blok sebelumnya sudah punya institusi
                prev_has_institution = any(
                    self.INSTITUTION_PATTERN.search(l)
                    for l in current_block
                )
                if prev_has_institution:
                    blocks.append(current_block)
                    current_block = []

            current_block.append(stripped)

        if current_block:
            blocks.append(current_block)

        return blocks

    # ── Private: Block Parsing ─────────────────────────────────────────────────

    def _parse_block(
        self,
        block: List[str],
        candidate_profile_id: int,
        sort_order: int
    ) -> Optional[CandidateEducation]:
        """Parse satu blok menjadi CandidateEducation."""
        if not block:
            return None

        edu = CandidateEducation(
            candidate_profile_id=candidate_profile_id,
            sort_order=sort_order
        )

        full_text = " ".join(block)

        # Ekstrak field dari full text block
        edu.start_date_text, edu.end_date_text = self._extract_years(full_text)
        edu.gpa_text        = self._extract_gpa(full_text)
        edu.education_level = self._detect_education_level(full_text)

        # Ekstrak institusi, degree, major baris per baris
        edu.institution_name, edu.degree_name, edu.major_name = \
            self._extract_institution_degree_major(block)

        return edu

    # ── Private: Field Extractors ──────────────────────────────────────────────

    def _extract_years(
        self, text: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Ekstrak tahun mulai dan selesai dari berbagai format."""
        match = self.YEAR_RANGE_PATTERN.search(text)
        if match:
            return match.group("start"), match.group("end")
        return None, None

    def _extract_gpa(self, text: str) -> Optional[str]:
        """Ekstrak nilai GPA/IPK dari teks."""
        match = self.GPA_PATTERN.search(text)
        if match:
            return match.group(1) or match.group(2)
        return None

    def _detect_education_level(self, text: str) -> Optional[str]:
        """Deteksi level pendidikan berdasarkan keyword."""
        for level, pattern in self.EDUCATION_LEVEL_PATTERNS:
            if pattern.search(text):
                return level
        return None

    def _extract_institution_degree_major(
        self, block: List[str]
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Ekstrak nama institusi, gelar, dan jurusan dari baris-baris blok.
        Strategi:
        - Baris yang mengandung keyword institusi → institution_name
        - Baris yang mengandung keyword degree/major → major_name
        - Baris pertama tanpa year → degree_name (jika belum ada)
        """
        institution = None
        degree      = None
        major       = None

        for line in block:
            # Bersihkan bullet, tahun, GPA dari baris untuk analisis
            cleaned = re.sub(r"^[•\-\*]\s*", "", line).strip()
            cleaned = self.YEAR_RANGE_PATTERN.sub("", cleaned).strip()
            cleaned = self.GPA_PATTERN.sub("", cleaned).strip()
            cleaned = re.sub(r"[–\-—|/,]+\s*$", "", cleaned).strip()
            cleaned = re.sub(r"^\s*[–\-—|/,]+", "", cleaned).strip()

            if not cleaned or len(cleaned) < 3:
                continue

            is_institution_line = bool(self.INSTITUTION_PATTERN.search(cleaned))
            is_degree_line      = bool(self.DEGREE_PATTERN.search(cleaned))

            if is_institution_line and not institution:
                institution = cleaned
            elif is_degree_line and not major:
                major = cleaned
            elif not degree and not is_institution_line and not is_degree_line:
                # Baris pertama tanpa keyword khusus → degree/program name
                if not re.match(r"^\d", cleaned):
                    degree = cleaned

        return institution, degree, major
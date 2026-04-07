"""
Service : ExperienceParser
Layer   : Infrastructure > Parsers > Regex
Fungsi  : Mengekstrak riwayat pengalaman kerja dari raw OCR text.
Phase   : 3 - Structured Candidate Data

Mendukung berbagai format CV:
    Format A: Date di baris pertama tersendiri
        "November 2022 – Desember 2022"
        "Sales Representative"
        "Big Ant Store | Bandung"

    Format B: Job Title dan Date di baris yang sama
        "Sales Representative : November 2022 – Desember 2022"
        "Big Ant Store – Telkom University | Bandung"

    Format C: Date di kolom kiri, detail di kolom kanan (layout 2 kolom)
        "Januari 2023 – sekarang    PT Melati Ritel, Medan"
        "                            Pramuniaga"

    Format D: Format internasional / Inggris
        "Software Engineer | Jan 2022 - Present"
        "Google, Jakarta"
"""

import re
from typing import List, Optional, Tuple
from src.domain.entities.candidate_experience import CandidateExperience


class ExperienceParser:

    # ── Section Headers ────────────────────────────────────────────────────────
    EXPERIENCE_SECTION_PATTERN = re.compile(
        r"^(?:"
        r"work\s+experience|pengalaman\s+kerja|riwayat\s+kerja"
        r"|project\s+experience|pengalaman\s+proyek"
        r"|organizational\s+experience|pengalaman\s+organisasi"
        r"|experience|pengalaman"
        r")$",
        re.IGNORECASE
    )

    # ── Section Enders ─────────────────────────────────────────────────────────
    # Section yang menandakan akhir dari experience section
    END_SECTION_PATTERN = re.compile(
        r"^(?:"
        r"(?:technical\s+)?skills?|keahlian|kompetensi|kemampuan"
        r"|hard\s+skill|soft\s+skill|technical\s+and\s+non"
        r"|pendidikan|education|riwayat\s+pendidikan"
        r"|sertifikasi|certifications?|training|seminar|pelatihan"
        r"|referensi|references?"
        r")$",
        re.IGNORECASE
    )

    # ── Date Range Patterns ────────────────────────────────────────────────────
    # Nama bulan Indonesia dan Inggris
    MONTH_NAMES = (
        r"januari|februari|maret|april|mei|juni|juli|agustus|september"
        r"|oktober|november|desember"
        r"|january|february|march|april|may|june|july|august|september"
        r"|october|november|december"
        r"|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec"
    )

    CURRENT_TERMS = r"sekarang|present|current|now|saat\s+ini|hingga\s+ini"

    # Pattern date range lengkap
    DATE_RANGE_PATTERN = re.compile(
        r"(?P<start>"
        r"(?:(?:" + MONTH_NAMES + r")\s+)?\d{4}"
        r")"
        r"\s*[–\-—]\s*"
        r"(?P<end>"
        r"(?:(?:" + MONTH_NAMES + r")\s+)?\d{4}"
        r"|" + CURRENT_TERMS +
        r")",
        re.IGNORECASE
    )

    # Pattern hanya tahun (2020-2022)
    YEAR_ONLY_RANGE_PATTERN = re.compile(
        r"(?P<start>\d{4})\s*[–\-—/|]\s*(?P<end>\d{4}|" + CURRENT_TERMS + r")",
        re.IGNORECASE
    )

    # ── Employment Type ────────────────────────────────────────────────────────
    EMPLOYMENT_TYPE_PATTERNS = {
        "internship": re.compile(
            r"\b(internship|magang|intern|praktik\s+kerja)\b", re.IGNORECASE
        ),
        "full-time": re.compile(
            r"\b(full[-\s]?time|penuh\s+waktu)\b", re.IGNORECASE
        ),
        "part-time": re.compile(
            r"\b(part[-\s]?time|paruh\s+waktu)\b", re.IGNORECASE
        ),
        "freelance": re.compile(
            r"\b(freelance|lepas|kontrak)\b", re.IGNORECASE
        ),
    }

    # ── Location Pattern ───────────────────────────────────────────────────────
    LOCATION_PATTERN = re.compile(
        r"[|,]\s*([A-Za-z\s]+(?:,\s*[A-Za-z\s]+)?)$",
        re.IGNORECASE
    )

    # ── Bullet / List Marker ───────────────────────────────────────────────────
    BULLET_PATTERN = re.compile(r"^[•\-\*✓√►▸]\s*")

    # ── Public Methods ─────────────────────────────────────────────────────────

    def extract(
        self,
        raw_text: str,
        candidate_profile_id: int
    ) -> List[CandidateExperience]:
        if not raw_text or not raw_text.strip():
            return []

        lines  = raw_text.splitlines()
        blocks = self._extract_experience_blocks(lines)

        experiences = []
        for sort_idx, block in enumerate(blocks):
            exp = self._parse_block(block, candidate_profile_id, sort_idx)
            if exp and exp.is_valid():
                experiences.append(exp)

        return experiences

    # ── Private: Block Extraction ──────────────────────────────────────────────

    def _extract_experience_blocks(
        self, lines: List[str]
    ) -> List[List[str]]:
        """
        Kumpulkan baris-baris dalam section experience,
        lalu kelompokkan menjadi blok per pengalaman.
        Blok baru dimulai setiap kali ditemukan date range.
        """
        blocks: List[List[str]]  = []
        current_block: List[str] = []
        in_experience_section    = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Masuk section experience
            if self.EXPERIENCE_SECTION_PATTERN.match(stripped):
                in_experience_section = True
                continue

            if not in_experience_section:
                continue

            # Keluar section experience
            if self.END_SECTION_PATTERN.match(stripped):
                # Cek apakah section baru ini adalah experience lain
                if self.EXPERIENCE_SECTION_PATTERN.match(stripped):
                    continue  # Tetap dalam konteks experience
                in_experience_section = False
                if current_block:
                    blocks.append(current_block)
                    current_block = []
                continue

            # Deteksi date range → mulai blok baru
            if self._has_date_range(stripped):
                if current_block:
                    blocks.append(current_block)
                current_block = [stripped]
            else:
                if current_block:
                    current_block.append(stripped)

        # Tambahkan blok terakhir
        if current_block:
            blocks.append(current_block)

        return blocks

    def _has_date_range(self, text: str) -> bool:
        """Cek apakah teks mengandung pola date range."""
        return bool(
            self.DATE_RANGE_PATTERN.search(text)
            or self.YEAR_ONLY_RANGE_PATTERN.search(text)
        )

    # ── Private: Block Parsing ─────────────────────────────────────────────────

    def _parse_block(
        self,
        block: List[str],
        candidate_profile_id: int,
        sort_order: int
    ) -> Optional[CandidateExperience]:
        """
        Parse satu blok menjadi CandidateExperience.
        Robust untuk berbagai format CV.
        """
        if not block:
            return None

        exp = CandidateExperience(
            candidate_profile_id=candidate_profile_id,
            sort_order=sort_order
        )

        description_lines: List[str] = []
        title_company_parsed         = False

        for i, line in enumerate(block):
            stripped = line.strip()
            if not stripped:
                continue

            # ── Coba ekstrak date range dari baris ini ─────────────────────────
            date_found, remaining = self._extract_date_range(stripped)
            if date_found:
                exp.start_date_text, exp.end_date_text = date_found
                exp.is_current = self._is_current_term(
                    exp.end_date_text or ""
                )

                # Cek apakah ada job title SEBELUM tanggal di baris yang sama
                # Format: "Sales Representative : November 2022 – Desember 2022"
                remaining = remaining.strip().strip(":–-—").strip()
                if remaining and not exp.job_title:
                    exp.job_title = remaining
                    exp.employment_type = self._detect_employment_type(remaining)
                continue

            # ── Baris tanpa date → coba parse sebagai title/company/desc ───────
            is_bullet = bool(self.BULLET_PATTERN.match(stripped))

            if not title_company_parsed and not is_bullet:
                # Coba parse sebagai baris title/company
                parsed = self._parse_title_company_line(stripped)
                if parsed:
                    title, company, location = parsed

                    if not exp.job_title and title:
                        exp.job_title = title
                        exp.employment_type = (
                            exp.employment_type
                            or self._detect_employment_type(title)
                        )
                    if not exp.company_name and company:
                        exp.company_name = company
                    if not exp.location_text and location:
                        exp.location_text = location

                    # Tandai title/company sudah di-parse setelah dapat company
                    if exp.company_name:
                        title_company_parsed = True
                    continue

            # ── Sisa baris → deskripsi ─────────────────────────────────────────
            cleaned = self.BULLET_PATTERN.sub("", stripped).strip()
            if cleaned and len(cleaned) > 5:
                description_lines.append(cleaned)

        if description_lines:
            exp.description_text = " | ".join(description_lines)

        return exp

    # ── Private: Date Extraction ───────────────────────────────────────────────

    def _extract_date_range(
        self, text: str
    ) -> Tuple[Optional[Tuple[str, str]], str]:
        """
        Ekstrak date range dari teks.
        Return: ((start_date, end_date), remaining_text)
        Jika tidak ditemukan, return (None, original_text)
        """
        # Coba date range dengan nama bulan
        match = self.DATE_RANGE_PATTERN.search(text)
        if match:
            start = match.group("start").strip()
            end   = match.group("end").strip()
            remaining = text[:match.start()] + text[match.end():]
            return (start, end), remaining.strip()

        # Coba year-only range
        match = self.YEAR_ONLY_RANGE_PATTERN.search(text)
        if match:
            start = match.group("start").strip()
            end   = match.group("end").strip()
            remaining = text[:match.start()] + text[match.end():]
            return (start, end), remaining.strip()

        return None, text

    def _is_current_term(self, text: str) -> bool:
        """Cek apakah teks menyatakan 'masih bekerja'."""
        current_pattern = re.compile(self.CURRENT_TERMS, re.IGNORECASE)
        return bool(current_pattern.search(text))

    # ── Private: Title/Company Parsing ────────────────────────────────────────

    def _parse_title_company_line(
        self, line: str
    ) -> Optional[Tuple[Optional[str], Optional[str], Optional[str]]]:
        """
        Parse baris yang berisi job title dan/atau company name.

        Mendukung format:
        - "Job Title – Company Name | Location"
        - "Job Title at Company Name, Location"
        - "Company Name | Location"
        - "Company Name, Location"
        - "Job Title"

        Return: (job_title, company_name, location) atau None
        """
        job_title    = None
        company_name = None
        location     = None

        # Ekstrak lokasi dari akhir baris (setelah | atau ,Kota)
        loc_match = self.LOCATION_PATTERN.search(line)
        if loc_match:
            location = loc_match.group(1).strip()
            line     = line[:loc_match.start()].strip()

        # Pisahkan job title dan company
        # Coba separator: –, -, —, " at ", " – "
        parts = re.split(r"\s*[–—]\s*|\s+at\s+", line, maxsplit=1)

        if len(parts) == 2:
            job_title    = parts[0].strip() or None
            company_name = parts[1].strip() or None
        elif line.strip():
            # Tidak ada separator → seluruh baris adalah job title atau company
            job_title = line.strip()

        return (job_title, company_name, location)

    # ── Private: Employment Type ───────────────────────────────────────────────

    def _detect_employment_type(self, text: str) -> Optional[str]:
        """Deteksi tipe employment dari teks."""
        for emp_type, pattern in self.EMPLOYMENT_TYPE_PATTERNS.items():
            if pattern.search(text):
                return emp_type
        return None
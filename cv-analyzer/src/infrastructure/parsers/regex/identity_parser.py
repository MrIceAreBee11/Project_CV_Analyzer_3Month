"""
Service : IdentityParser
Layer   : Infrastructure > Parsers > Regex
Fungsi  : Mengekstrak identitas dasar kandidat dari raw OCR text
          menggunakan pendekatan regex dan heuristik sederhana.
Phase   : 2 - Basic Parser

Yang diekstrak:
- full_name     : dari baris awal dokumen
- email         : pola regex standar email
- phone_number  : pola nomor telepon Indonesia & internasional
- current_location / address_text : deteksi kata kunci lokasi
- linkedin_url  : pola URL linkedin.com
- github_url    : pola URL github.com
"""

import re
from typing import Optional

from matplotlib import lines, text
from src.domain.entities.candidate_profile import CandidateProfile


class IdentityParser:
    """
    Parser berbasis regex untuk mengekstrak identitas kandidat.
    Mengimplementasikan logika ekstraksi tanpa bergantung pada
    framework atau library ML apapun.
    """

    # ── Regex Patterns ─────────────────────────────────────────────────────────

    # Email: standar RFC format
    EMAIL_PATTERN = re.compile(
        r"[a-zA-Z0-9._%+\-]+"
        r"@[a-zA-Z0-9\-]+(?:\.[a-zA-Z0-9\-]+)+"
        r"\.[a-zA-Z]{2,}",
        re.IGNORECASE,
    )

    # Phone: mendukung format Indonesia (+62, 08xx) dan internasional
    PHONE_PATTERN = re.compile(
        r"(?:"
        # Indonesia mobile: +62 8xx... atau 08xx...
        r"(?:(?:\+62|62)[\s\-]?(?:\(0\))?[\s\-]?8\d{2}[\s\-]?\d{3,4}[\s\-]?\d{3,4}"
        r"|08\d{2}[\s\-]?\d{3,4}[\s\-]?\d{3,4}"
        r")"
        r"|"
        # Landline dengan kode area, contoh: (021) 1234567 atau 021-1234567
        r"(?:\(\d{2,4}\)[\s\-]?\d{5,8}|\d{2,4}[\s\-]\d{5,8})"
        r"|"
        # Internasional umum: +<country><rest> minimal total 8 digit
        r"(?:\+\d{1,3}[\s\-]?\d{6,12})"
        r")"
    )

    # LinkedIn URL
    LINKEDIN_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+/?",
        re.IGNORECASE
    )

    # GitHub URL
    GITHUB_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?github\.com/[\w\-]+/?",
        re.IGNORECASE
    )

    # Portfolio / Website personal
    PORTFOLIO_PATTERN = re.compile(
        r"(?:https?://)?(?:www\.)?"
        r"(?!linkedin)(?!inkedin)(?!github)(?!facebook)(?!twitter)(?!instagram)"
        r"(?!behance)(?!dribbble)"
        r"[\w\-]+(?:\.[\w\-]+)*\."
        r"(?:com|id|io|dev|me|co\.id|net|app|xyz|studio|site|page|tech|digital|online|space|website|info|biz|pro|tv|cc|us|uk)"
        r"(?:/[\w\-/]*)?",
        re.IGNORECASE
    )

    NON_LOCATION_KEYWORDS = [
    "store", "university", "telkom", "institute", "school",
    "pt ", "cv ", "tbk", "ltd", "inc", "corp",
    "internship", "intern", "magang", "kerja",
    ]

    # Kata kunci penanda section lokasi
    LOCATION_KEYWORDS = [
        "jakarta", "bandung", "surabaya", "yogyakarta", "medan",
        "semarang", "depok", "tangerang", "bekasi", "bogor",
        "malang", "makassar", "palembang", "bali", "denpasar",
        "indonesia", "jawa", "sumatra", "kalimantan","sukabumi",
        "cimahi", "garut", "tasikmalaya", "cirebon", "purwakarta",
        "subang", "karawang", "serang", "pandeglang", "lembang",
        "ciwidey", "puncak", "anyer", "banten", "sidoarjo", "gresik",
        "samarinda", "balikpapan", "banjarmasin", "pontianak",
        "palangkaraya", "manado", "gorontalo", "ambon", "papua","maluku",
        "sulawesi","aceh","lombok","sumbawa","flores","timor"
    ]

    # Kata kunci yang menandakan baris BUKAN nama orang
    NON_NAME_KEYWORDS = [
        "curriculum", "vitae", "resume", "cv", "profile",
        "email", "phone", "tel", "address", "linkedin",
        "github", "portfolio", "website", "objective",
        "summary", "skills", "education", "experience",
        "http", "www", "@", ":",
        # Section headers Indonesia
        "ringkasan", "keterampilan", "pendidikan", "pengalaman",
        "sertifikasi", "pelatihan", "organisasi", "referensi",
        # Jabatan umum yang sering jadi header CV
        "pramuniaga", "manager", "engineer", "developer",
        "designer", "analyst", "staff", "intern", "magang",
        "koordinator", "supervisor", "direktur", "kepala",
        "enthusiast", "specialist", "consultant", "officer",
    ]

    # ── Public Methods ─────────────────────────────────────────────────────────

    def extract(self, raw_text: str) -> CandidateProfile:
        """
        Entry point utama — ekstrak semua identitas dari raw text.

        Args:
            raw_text: teks mentah hasil OCR

        Returns:
            CandidateProfile berisi data identitas yang berhasil diekstrak.
            Field yang tidak ditemukan bernilai None.
        """
        if not raw_text or not raw_text.strip():
            return CandidateProfile()

        cleaned_text = self._clean_text(raw_text)
        lines        = [l.strip() for l in cleaned_text.splitlines() if l.strip()]

        profile = CandidateProfile()
        profile.full_name        = self._extract_name(lines)
        profile.email            = self._extract_email(cleaned_text)
        profile.phone_number     = self._extract_phone(cleaned_text)
        profile.linkedin_url     = self._extract_linkedin(cleaned_text)
        profile.github_url       = self._extract_github(cleaned_text)
        profile.portfolio_url    = self._extract_portfolio(cleaned_text)
        profile.current_location = self._extract_location(cleaned_text)
        profile.professional_summary = self._extract_summary(lines)
        profile.raw_text         = raw_text

        return profile

    # ── Private: Clean ─────────────────────────────────────────────────────────

    def _clean_text(self, text: str) -> str:
        """
        Bersihkan noise umum dari hasil OCR:
        - karakter non-printable
        - spasi berlebih
        - baris kosong berulang
        """
        # Hapus karakter non-printable kecuali newline dan tab
        text = re.sub(r"[^\x20-\x7E\n\t\u00C0-\u024F]", " ", text)
        # Normalisasi spasi berlebih dalam satu baris
        text = re.sub(r"[ \t]+", " ", text)
        # Normalisasi baris kosong berulang
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    # ── Private: Name ──────────────────────────────────────────────────────────

    def _extract_name(self, lines: list) -> Optional[str]:
    
        for i, line in enumerate(lines[:10]):
            line_lower = line.lower()

            # Skip baris yang mengandung keyword bukan nama
            if any(kw in line_lower for kw in self.NON_NAME_KEYWORDS):
                continue

            # ← TAMBAHKAN INI: skip baris yang mengandung nama kota/lokasi
            if any(kw in line_lower for kw in self.LOCATION_KEYWORDS):
                continue

            # Skip baris terlalu pendek atau terlalu panjang
            if len(line) < 3 or len(line) > 60:
                continue

            # Skip baris yang mengandung angka
            if re.search(r"\d", line):
                continue

            words = line.split()

            if 2 <= len(words) <= 5:
                if all(w[0].isupper() or w.isupper() for w in words if w):
                    return line.strip()

            if len(words) == 1 and line[0].isupper():
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    next_lower = next_line.lower()

                if any(kw in next_lower for kw in self.LOCATION_KEYWORDS):
                    continue
                if any(kw in next_lower for kw in self.NON_NAME_KEYWORDS):
                    continue
                if re.search(r"\d", next_line):
                    continue

            next_words = next_line.split()
            if 1 <= len(next_words) <= 3:
                combined = f"{line.strip()} {next_line}"
                if all(w[0].isupper() or w.isupper() for w in combined.split() if w):
                    return combined

        return None

    # ── Private: Email ─────────────────────────────────────────────────────────

    def _extract_email(self, text: str) -> Optional[str]:
        """Ekstrak email pertama yang ditemukan di text."""
        match = self.EMAIL_PATTERN.search(text)
        if not match:
            return None

        email = match.group(0).strip().lower()
        # Bersihkan tanda baca yang sering nempel akibat format CV
        # contoh: "email: nama@gmail.com," -> koma ikut ke-capture
        email = email.rstrip(".,;()[]")

        return email

    # ── Private: Phone ─────────────────────────────────────────────────────────

    def _extract_phone(self, text: str) -> Optional[str]:
        """
        Ekstrak nomor telepon pertama yang ditemukan.
        Normalisasi: hapus spasi dan tanda hubung berlebih.
        """
        match = self.PHONE_PATTERN.search(text)
        if not match:
            return None

        phone = match.group(0)
        # Normalisasi: hapus spasi dan strip
        phone = re.sub(r"[\s\-\(\)]", "", phone)
        return phone

    # ── Private: Social Links ──────────────────────────────────────────────────

    def _extract_linkedin(self, text: str) -> Optional[str]:
        """Ekstrak URL LinkedIn jika ada."""
        match = self.LINKEDIN_PATTERN.search(text)
        return match.group(0) if match else None

    def _extract_github(self, text: str) -> Optional[str]:
        """Ekstrak URL GitHub jika ada."""
        match = self.GITHUB_PATTERN.search(text)
        return match.group(0) if match else None

    def _extract_portfolio(self, text: str) -> Optional[str]:
        match = self.PORTFOLIO_PATTERN.search(text)
        if not match:
            return None
 
        url = match.group(0).strip()
        lower_url = url.lower()
 
        # Reject jika URL mengandung variasi linkedin (termasuk OCR error)
        excluded = [
            "linkedin", "inkedin", "nkedin", "edin.com",
            "email.com", "gmail.com", "yahoo.com",
            "hotmail.com", "outlook.com"
        ]
        if any(ex in lower_url for ex in excluded):
            return None
 
        # Normalisasi: kalau belum ada skema, tambahkan https://
        if not lower_url.startswith("http://") and not lower_url.startswith("https://"):
            url = "https://" + url.lstrip("/")
 
        return url
 

    # ── Private: Location ──────────────────────────────────────────────────────

    def _extract_location(self, text: str) -> Optional[str]:
        """
        Deteksi lokasi dari header CV.
        Strategi: cari bagian setelah karakter '|' di 10 baris pertama
        yang mengandung keyword lokasi.
        """
        lines = text.splitlines()

        # Strategi 1: ambil bagian setelah '|' di baris header
        for line in lines[:10]:
            if "|" in line:
                parts = line.split("|")
                for part in parts:
                    part = part.strip()
                    part_lower = part.lower()
                    if any(kw in part_lower for kw in self.LOCATION_KEYWORDS):
                        # Pastikan bukan baris experience (ada kata company)
                        if not any(kw in part_lower for kw in [
                            "store", "university", "telkom", "institute",
                            "pt ", "ltd", "inc", "corp", "intern", "sman",
                            "smk", "sma", "sd ", "smp"
                        ]):
                            return part

        # Strategi 2: cari baris pendek yang hanya berisi lokasi
        for line in lines[:10]:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()

            if re.search(r"\d{6,}", line_stripped):
                continue
            if any(kw in line_lower for kw in [
                "store", "university", "telkom", "sman", "smk",
                "pt ", "ltd", "inc", "corp", "intern"
            ]):
                continue
            if any(kw in line_lower for kw in self.LOCATION_KEYWORDS):
                if len(line_stripped) < 60:
                    return line_stripped

        return None
    
    def _extract_summary(self, lines: list) -> Optional[str]:
        """
        Deteksi paragraf professional summary.
        Gabungkan semua baris panjang yang berurutan di area summary.
        """
        summary_lines = []
        collecting = False

        for i, line in enumerate(lines[:40]):
            stripped = line.strip()

            # Mulai collect jika ketemu baris panjang (>80 char)
            if len(stripped) > 80 and not collecting:
                collecting = True

            if collecting:
                if len(stripped) > 30:
                    summary_lines.append(stripped)
                elif summary_lines:
                    # Baris pendek setelah collect = summary selesai
                    break

        if summary_lines:
            return " ".join(summary_lines)
        return None
"""
Service : SkillsParser
Layer   : Infrastructure > Parsers > Regex
Fungsi  : Mengekstrak daftar skill dari raw OCR text
          dengan mencocokkan keyword dari tabel skill_dictionaries.
Phase   : 2 - Basic Parser

Strategi:
1. Ambil semua skill aktif dari database (skill_dictionaries)
2. Untuk setiap skill, cek apakah skill_name atau salah satu alias-nya
   muncul di raw text
3. Deteksi section asal skill ditemukan (Skills, Experience, dll)
4. Hindari duplikasi skill yang sama
5. Hitung confidence score sederhana berdasarkan lokasi penemuan
"""

import re
import json
from typing import List, Optional
from sqlalchemy.orm import Session

from src.domain.entities.candidate_skill import CandidateSkill
from src.infrastructure.persistence.models.skill_dictionary_model import (
    SkillDictionaryModel
)


class SkillsParser:
    """
    Parser skill berbasis dictionary matching.
    Membaca skill aktif dari database lalu mencocokkan dengan raw text.
    """

    # ── Section Headers yang umum ditemukan di CV ──────────────────────────────
    SECTION_PATTERNS = {
        "summary": re.compile(
        r"summary|profil|profile|about\s+me|tentang\s+saya|objektif|objective|mine|ringkasan|deskripsi|gambaran\s+umum",
        re.IGNORECASE
        ),
        "skills": re.compile(
        r"(?:technical\s+)?skills?|keahlian|kompetensi|kemampuan|keterampilan|skill|skills|expertise|proficiency|qualifications|abilities"
        r"|hard\s+skill|soft\s+skill|technical\s+and\s+non",
        re.IGNORECASE
        ),
        "experience": re.compile(
            r"(?:work\s+)?experience|pengalaman(?:\s+kerja)?|riwayat\s+kerja",
            re.IGNORECASE
        ),
        "education": re.compile(
            r"education|pendidikan|riwayat\s+pendidikan",
            re.IGNORECASE
        ),
        "projects": re.compile(
            r"projects?|proyek|portofolio",
            re.IGNORECASE
        ),
        "certifications": re.compile(
            r"certifications?|sertifikasi|sertifikat|lisensi|kualifikasi|penghargaan|training|seminar|kursus|pelatihan|workshop|webinar",
            re.IGNORECASE
        ),
    }

    # Confidence score berdasarkan section tempat skill ditemukan
    SECTION_CONFIDENCE = {
        "skills":         1.0,    # Ditemukan di section skills → paling relevan
        "summary":        0.9,
        "projects":       0.85,
        "experience":     0.75,
        "certifications": 0.7,
        "education":      0.6,
        "unknown":        0.5,    # Tidak diketahui dari section mana
    }

    # ── Constructor ────────────────────────────────────────────────────────────

    def __init__(self, db: Session):
        """
        Args:
            db: SQLAlchemy session untuk membaca skill_dictionaries
        """
        self.db = db
        self._skill_data: Optional[List[dict]] = None  # cache

    # ── Public Methods ─────────────────────────────────────────────────────────

    def extract(
        self,
        raw_text: str,
        candidate_profile_id: int
    ) -> List[CandidateSkill]:
        """
        Entry point utama — ekstrak semua skill dari raw text.

        Args:
            raw_text             : teks mentah hasil OCR
            candidate_profile_id : ID candidate profile pemilik skill

        Returns:
            List CandidateSkill tanpa duplikasi.
            List kosong jika tidak ada skill yang ditemukan.
        """
        if not raw_text or not raw_text.strip():
            return []

        skill_dictionary = self._load_skill_dictionary()
        if not skill_dictionary:
            return []

        # Deteksi sections untuk context pencarian
        sections = self._detect_sections(raw_text)

        found_skills: List[CandidateSkill] = []
        seen_normalized: set = set()  # hindari duplikasi

        for skill_entry in skill_dictionary:
            skill_name       = skill_entry["skill_name"]
            normalized_name  = skill_entry["normalized_skill_name"]
            category         = skill_entry["category"]
            aliases          = skill_entry["aliases"]

            # Skip jika skill ini sudah ditemukan sebelumnya
            if normalized_name in seen_normalized:
                continue

            # Cek apakah skill ditemukan di text
            match_result = self._find_skill_in_text(
                raw_text=raw_text,
                skill_name=skill_name,
                aliases=aliases,
                sections=sections,
            )

            if match_result is None:
                continue

            source_text, source_section = match_result
            confidence = self.SECTION_CONFIDENCE.get(source_section, 0.5)

            skill = CandidateSkill(
                candidate_profile_id=candidate_profile_id,
                skill_name=skill_name,
                skill_category=category,
                source_text=source_text[:200] if source_text else None,
                source_section=source_section,
                confidence_score=confidence,
                is_primary=(source_section == "skills"),
            )

            found_skills.append(skill)
            seen_normalized.add(normalized_name)

        return found_skills

    # ── Private: Load Dictionary ───────────────────────────────────────────────

    def _load_skill_dictionary(self) -> List[dict]:
        """
        Ambil semua skill aktif dari database.
        Cache di memory agar tidak query ulang untuk setiap CV.
        """
        if self._skill_data is not None:
            return self._skill_data

        rows = (
            self.db.query(SkillDictionaryModel)
            .filter(SkillDictionaryModel.is_active == True)
            .all()
        )

        self._skill_data = []
        for row in rows:
            aliases = []
            if (str(row.aliases_json)):
                try:
                    aliases = json.loads(str(row.aliases_json))
                except (json.JSONDecodeError, TypeError):
                    aliases = []

            self._skill_data.append({
                "skill_name":            row.skill_name,
                "normalized_skill_name": row.normalized_skill_name,
                "category":              row.category,
                "aliases":               aliases,
            })

        return self._skill_data

    # ── Private: Section Detection ─────────────────────────────────────────────

    def _detect_sections(self, raw_text: str) -> dict:
        """
        Deteksi posisi (line index) setiap section di dalam raw text.

        Returns:
            Dict berisi {section_name: [list of line indices]}
        """
        lines = raw_text.splitlines()
        sections = {name: [] for name in self.SECTION_PATTERNS}

        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            for section_name, pattern in self.SECTION_PATTERNS.items():
                if pattern.match(stripped):
                    sections[section_name].append(idx)

        return sections

    # ── Private: Find Skill ────────────────────────────────────────────────────

    def _find_skill_in_text(
        self,
        raw_text: str,
        skill_name: str,
        aliases: List[str],
        sections: dict,
    ) -> Optional[tuple]:
        """
        Cari satu skill di dalam raw text.
        Cek skill_name dan semua alias-nya.

        Returns:
            Tuple (source_text, source_section) jika ditemukan.
            None jika tidak ditemukan.
        """
        # Semua variasi nama yang akan dicek
        keywords = [skill_name] + aliases

        lines = raw_text.splitlines()

        for line_idx, line in enumerate(lines):
            for keyword in keywords:
                # Gunakan word boundary agar "Go" tidak match "Google"
                pattern = re.compile(
                    r"(?<![a-zA-Z0-9])"
                    + re.escape(keyword)
                    + r"(?![a-zA-Z0-9])",
                    re.IGNORECASE
                )
                if pattern.search(line):
                    section = self._get_section_for_line(line_idx, sections)
                    return (line.strip(), section)

        return None

    def _get_section_for_line(
        self,
        line_idx: int,
        sections: dict
    ) -> str:
        """
        Tentukan section mana yang paling dekat sebelum baris ini.

        Args:
            line_idx: index baris saat ini
            sections: dict hasil _detect_sections

        Returns:
            Nama section (str), default "unknown"
        """
        closest_section = "unknown"
        closest_distance = float("inf")

        for section_name, indices in sections.items():
            for section_line_idx in indices:
                # Section harus berada SEBELUM baris ini
                if section_line_idx <= line_idx:
                    distance = line_idx - section_line_idx
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_section = section_name
        # Fallback: jika masih unknown DAN baris ada di area awal dokumen
        # kemungkinan besar skill ditemukan di paragraf summary/header
        if closest_section == "unknown" and line_idx <= 30:
          closest_section = "summary"

        return closest_section
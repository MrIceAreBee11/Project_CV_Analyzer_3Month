"""
Alembic Migration: Phase 2 - Basic Parser Tables
Revision  : f7e8d9c0b1a2
Revises   : 5b1d161f4d6c
Create Date: 2025-04-01

Tabel yang dibuat:
    - skill_dictionaries  : master data dictionary skill
    - candidate_profiles  : hasil parsing kandidat
    - candidate_skills    : skill hasil ekstraksi per kandidat
"""

from alembic import op
import sqlalchemy as sa

# ── Revision Identifiers ───────────────────────────────────────────────────────
revision = "f7e8d9c0b1a2"
down_revision: str = '5b1d161f4d6c'  # ⚠️ GANTI dengan revision ID migration Phase 1 kamu
branch_labels = None
depends_on = None


# ── Upgrade: Buat Tabel Baru ───────────────────────────────────────────────────
def upgrade() -> None:

    # ── 1. Tabel skill_dictionaries ────────────────────────────────────────────
    # Dibuat duluan karena tidak ada FK ke tabel lain
    op.create_table(
        "skill_dictionaries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("skill_name", sa.String(255), nullable=False),
        sa.Column("normalized_skill_name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("aliases_json", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("skill_name", name="uq_skill_dictionaries_skill_name"),
    )

    # ── 2. Tabel candidate_profiles ───────────────────────────────────────────
    op.create_table(
        "candidate_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", sa.String(36), nullable=False),

        # FK ke cv_documents (harus sudah ada dari Phase 1)
        sa.Column("cv_document_id", sa.Integer(), nullable=False),

        # Identitas kandidat
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone_number", sa.String(50), nullable=True),
        sa.Column("alternate_phone_number", sa.String(50), nullable=True),
        sa.Column("current_location", sa.String(255), nullable=True),
        sa.Column("address_text", sa.Text(), nullable=True),

        # Informasi profesional
        sa.Column("professional_summary", sa.Text(), nullable=True),
        sa.Column("date_of_birth_text", sa.String(100), nullable=True),
        sa.Column("total_experience_text", sa.String(255), nullable=True),
        sa.Column("estimated_total_experience_months", sa.Integer(), nullable=True),
        sa.Column("latest_job_title", sa.String(255), nullable=True),
        sa.Column("latest_company_name", sa.String(255), nullable=True),

        # Social links
        sa.Column("linkedin_url", sa.String(500), nullable=True),
        sa.Column("github_url", sa.String(500), nullable=True),
        sa.Column("portfolio_url", sa.String(500), nullable=True),

        # Parser metadata
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("parser_version", sa.String(50), nullable=True, server_default="1.0.0"),
        sa.Column("parser_status", sa.String(50), nullable=True, server_default="pending"),
        sa.Column("parser_notes", sa.Text(), nullable=True),

        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid", name="uq_candidate_profiles_uuid"),
        sa.UniqueConstraint(
            "cv_document_id",
            name="uq_candidate_profiles_cv_document_id"
        ),
        sa.ForeignKeyConstraint(
            ["cv_document_id"],
            ["cv_documents.id"],
            name="fk_candidate_profiles_cv_document_id",
            ondelete="CASCADE"
        ),
    )

    # Index untuk pencarian kandidat (dipakai di Phase 2 search)
    op.create_index(
        "ix_candidate_profiles_email",
        "candidate_profiles",
        ["email"]
    )
    op.create_index(
        "ix_candidate_profiles_phone_number",
        "candidate_profiles",
        ["phone_number"]
    )
    op.create_index(
        "ix_candidate_profiles_parser_status",
        "candidate_profiles",
        ["parser_status"]
    )

    # ── 3. Tabel candidate_skills ──────────────────────────────────────────────
    op.create_table(
        "candidate_skills",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),

        # FK ke candidate_profiles
        sa.Column("candidate_profile_id", sa.Integer(), nullable=False),

        # Data skill
        sa.Column("skill_name", sa.String(255), nullable=False),
        sa.Column("skill_category", sa.String(100), nullable=True),
        sa.Column("source_text", sa.Text(), nullable=True),
        sa.Column("source_section", sa.String(100), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="0"),

        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=False
        ),

        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["candidate_profile_id"],
            ["candidate_profiles.id"],
            name="fk_candidate_skills_candidate_profile_id",
            ondelete="CASCADE"
        ),
    )

    # Index untuk filter skill berdasarkan nama
    op.create_index(
        "ix_candidate_skills_skill_name",
        "candidate_skills",
        ["skill_name"]
    )
    op.create_index(
        "ix_candidate_skills_candidate_profile_id",
        "candidate_skills",
        ["candidate_profile_id"]
    )


# ── Downgrade: Hapus Tabel ─────────────────────────────────────────────────────
def downgrade() -> None:
    # Urutan drop harus kebalikan dari create (ikuti FK dependency)
    op.drop_index("ix_candidate_skills_candidate_profile_id", table_name="candidate_skills")
    op.drop_index("ix_candidate_skills_skill_name", table_name="candidate_skills")
    op.drop_table("candidate_skills")

    op.drop_index("ix_candidate_profiles_parser_status", table_name="candidate_profiles")
    op.drop_index("ix_candidate_profiles_phone_number", table_name="candidate_profiles")
    op.drop_index("ix_candidate_profiles_email", table_name="candidate_profiles")
    op.drop_table("candidate_profiles")

    op.drop_table("skill_dictionaries")
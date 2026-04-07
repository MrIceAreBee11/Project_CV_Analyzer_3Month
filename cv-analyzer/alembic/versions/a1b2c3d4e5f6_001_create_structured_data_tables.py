"""
Alembic Migration: Phase 3 - Structured Candidate Data Tables
Revision  : a1b2c3d4e5f6
Revises   : f7e8d9c0b1a2
Create Date: 2025-04-02

Tabel yang dibuat:
    - candidate_experiences  : riwayat pengalaman kerja
    - candidate_educations   : riwayat pendidikan
    - candidate_certifications: sertifikasi kandidat
"""

from alembic import op
import sqlalchemy as sa

# ── Revision Identifiers ───────────────────────────────────────────────────────
revision    = "a1b2c3d4e5f6"
down_revision = "f7e8d9c0b1a2"  # ← revision ID migration Phase 2
branch_labels = None
depends_on    = None


def upgrade() -> None:

    # ── 1. Tabel candidate_experiences ────────────────────────────────────────
    op.create_table(
        "candidate_experiences",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("candidate_profile_id", sa.Integer(), nullable=False),
        sa.Column("company_name",     sa.String(255), nullable=True),
        sa.Column("job_title",        sa.String(255), nullable=True),
        sa.Column("employment_type",  sa.String(100), nullable=True),
        sa.Column("location_text",    sa.String(255), nullable=True),
        sa.Column("start_date_text",  sa.String(100), nullable=True),
        sa.Column("end_date_text",    sa.String(100), nullable=True),
        sa.Column("is_current",       sa.Boolean(),   nullable=False, server_default="0"),
        sa.Column("duration_text",    sa.String(100), nullable=True),
        sa.Column("description_text", sa.Text(),      nullable=True),
        sa.Column("sort_order",       sa.Integer(),   nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["candidate_profile_id"], ["candidate_profiles.id"],
            name="fk_candidate_experiences_profile_id",
            ondelete="CASCADE"
        ),
    )
    op.create_index("ix_candidate_experiences_profile_id", "candidate_experiences", ["candidate_profile_id"])

    # ── 2. Tabel candidate_educations ──────────────────────────────────────────
    op.create_table(
        "candidate_educations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("candidate_profile_id", sa.Integer(), nullable=False),
        sa.Column("institution_name", sa.String(255), nullable=True),
        sa.Column("degree_name",      sa.String(255), nullable=True),
        sa.Column("major_name",       sa.String(255), nullable=True),
        sa.Column("education_level",  sa.String(50),  nullable=True),
        sa.Column("start_date_text",  sa.String(100), nullable=True),
        sa.Column("end_date_text",    sa.String(100), nullable=True),
        sa.Column("gpa_text",         sa.String(50),  nullable=True),
        sa.Column("description_text", sa.Text(),      nullable=True),
        sa.Column("sort_order",       sa.Integer(),   nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["candidate_profile_id"], ["candidate_profiles.id"],
            name="fk_candidate_educations_profile_id",
            ondelete="CASCADE"
        ),
    )
    op.create_index("ix_candidate_educations_profile_id", "candidate_educations", ["candidate_profile_id"])

    # ── 3. Tabel candidate_certifications ──────────────────────────────────────
    op.create_table(
        "candidate_certifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("candidate_profile_id",  sa.Integer(),    nullable=False),
        sa.Column("certification_name",    sa.String(255),  nullable=True),
        sa.Column("issuer_name",           sa.String(255),  nullable=True),
        sa.Column("issue_date_text",       sa.String(100),  nullable=True),
        sa.Column("expiration_date_text",  sa.String(100),  nullable=True),
        sa.Column("credential_id",         sa.String(255),  nullable=True),
        sa.Column("credential_url",        sa.String(500),  nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["candidate_profile_id"], ["candidate_profiles.id"],
            name="fk_candidate_certifications_profile_id",
            ondelete="CASCADE"
        ),
    )
    op.create_index("ix_candidate_certifications_profile_id", "candidate_certifications", ["candidate_profile_id"])


def downgrade() -> None:
    op.drop_index("ix_candidate_certifications_profile_id", table_name="candidate_certifications")
    op.drop_table("candidate_certifications")

    op.drop_index("ix_candidate_educations_profile_id", table_name="candidate_educations")
    op.drop_table("candidate_educations")

    op.drop_index("ix_candidate_experiences_profile_id", table_name="candidate_experiences")
    op.drop_table("candidate_experiences")
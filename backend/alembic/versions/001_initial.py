"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-10-29

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("full_name", sa.String(128), nullable=False, server_default=""),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("admin", "staff", name="userrole"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patient_code", sa.String(32), nullable=False),
        sa.Column("full_name", sa.String(128), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("age_years", sa.Integer(), nullable=True),
        sa.Column(
            "sex",
            sa.Enum("male", "female", "other", "unknown", name="sex"),
            nullable=False,
        ),
        sa.Column("phone", sa.String(32), nullable=False, server_default=""),
        sa.Column("address", sa.Text(), nullable=False, server_default=""),
        sa.Column("external_id", sa.String(64), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_patients_patient_code", "patients", ["patient_code"], unique=True)
    op.create_index("ix_patients_full_name", "patients", ["full_name"])

    op.create_table(
        "doctors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(128), nullable=False),
        sa.Column("specialty", sa.String(128), nullable=False, server_default=""),
        sa.Column("phone", sa.String(32), nullable=False, server_default=""),
        sa.Column("email", sa.String(128), nullable=False, server_default=""),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_doctors_full_name", "doctors", ["full_name"])

    op.create_table(
        "test_definitions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(32), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("sample_type", sa.String(64), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_test_definitions_code", "test_definitions", ["code"], unique=True)

    op.create_table(
        "test_parameters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "test_definition_id",
            sa.Integer(),
            sa.ForeignKey("test_definitions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code", sa.String(32), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("unit", sa.String(32), nullable=False, server_default=""),
        sa.Column("reference_text", sa.String(255), nullable=False, server_default=""),
        sa.Column("reference_min", sa.Float(), nullable=True),
        sa.Column("reference_max", sa.Float(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("test_definition_id", "code", name="uq_param_code"),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_number", sa.String(32), nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("doctor_id", sa.Integer(), sa.ForeignKey("doctors.id"), nullable=True),
        sa.Column(
            "status",
            sa.Enum("registered", "in_progress", "completed", name="orderstatus"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("ordered_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_orders_order_number", "orders", ["order_number"], unique=True)

    op.create_table(
        "order_tests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "order_id",
            sa.Integer(),
            sa.ForeignKey("orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "test_definition_id",
            sa.Integer(),
            sa.ForeignKey("test_definitions.id"),
            nullable=False,
        ),
        sa.UniqueConstraint("order_id", "test_definition_id", name="uq_order_test"),
    )

    op.create_table(
        "result_values",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "order_test_id",
            sa.Integer(),
            sa.ForeignKey("order_tests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "test_parameter_id",
            sa.Integer(),
            sa.ForeignKey("test_parameters.id"),
            nullable=False,
        ),
        sa.Column("value_text", sa.String(128), nullable=False, server_default=""),
        sa.Column("value_numeric", sa.Float(), nullable=True),
        sa.Column("flag", sa.String(16), nullable=False, server_default=""),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.UniqueConstraint("order_test_id", "test_parameter_id", name="uq_result_param"),
    )

    op.create_table(
        "clinic_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "clinic_name",
            sa.String(255),
            nullable=False,
            server_default="Open Diagnostic Lab",
        ),
        sa.Column("address", sa.Text(), nullable=False, server_default=""),
        sa.Column("phone", sa.String(64), nullable=False, server_default=""),
        sa.Column(
            "footer",
            sa.Text(),
            nullable=False,
            server_default="This report is computer generated.",
        ),
        sa.Column("logo_url", sa.String(512), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_table("clinic_settings")
    op.drop_table("result_values")
    op.drop_table("order_tests")
    op.drop_table("orders")
    op.drop_table("test_parameters")
    op.drop_table("test_definitions")
    op.drop_table("doctors")
    op.drop_table("patients")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS orderstatus")
    op.execute("DROP TYPE IF EXISTS sex")
    op.execute("DROP TYPE IF EXISTS userrole")

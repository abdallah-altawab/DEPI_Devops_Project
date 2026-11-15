
"""create appointments table"""

from alembic import op
import sqlalchemy as sa


revision = "6fff5aa1c94c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patient_name", sa.String(length=100), nullable=False),
        sa.Column(
            "appointment_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
    )

    op.create_index(
        "ix_appointments_id",
        "appointments",
        ["id"],
    )


def downgrade():
    op.drop_index(
        "ix_appointments_id",
        table_name="appointments",
    )
    op.drop_table("appointments")

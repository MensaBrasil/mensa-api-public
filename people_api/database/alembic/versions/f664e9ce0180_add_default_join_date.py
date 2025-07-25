"""add_default_join_date

Revision ID: f664e9ce0180
Revises: 37efd1521b12
Create Date: 2024-12-17 17:55:44.001005

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f664e9ce0180"
down_revision: str | None = "37efd1521b12"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    # ### commands manually created ###
    op.alter_column(
        table_name="registration",
        column_name="join_date",
        schema="public",
        server_default=sa.text("CURRENT_DATE"),
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    # ### commands manually created ###
    op.alter_column(
        table_name="registration", column_name="join_date", schema="public", server_default=None
    )

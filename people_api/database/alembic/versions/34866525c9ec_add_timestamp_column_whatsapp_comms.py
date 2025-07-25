"""add timestamp column whatsapp_comms

Revision ID: 34866525c9ec
Revises: 31cf9aebbbe8
Create Date: 2024-12-14 01:30:39.003027

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "34866525c9ec"
down_revision: str | None = "31cf9aebbbe8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "whatsapp_comms",
        sa.Column(
            "timestamp", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("whatsapp_comms", "timestamp")
    # ### end Alembic commands ###

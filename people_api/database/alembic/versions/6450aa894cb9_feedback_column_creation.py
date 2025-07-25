"""Feedback column creation

Revision ID: 6450aa894cb9
Revises: 6dda2e6dc27f
Create Date: 2025-05-15 10:32:23.003958

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '6450aa894cb9'
down_revision: Union[str, None] = '6dda2e6dc27f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('feedbacks',
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('registration_id', sa.Integer(), nullable=True),
    sa.Column('feedback_text', sqlmodel.sql.sqltypes.AutoString(length=1200), nullable=True),
    sa.Column('feedback_target', sa.Enum('CHATBOT', 'WHATSAPP', 'MOBILE_APP', 'SECRETARIA', 'GESTAO', name='feedbacktargets'), nullable=False),
    sa.Column('feedback_type', sa.Enum('NEUTRAL', 'POSITIVE', 'NEGATIVE', 'FEATURE_REQUEST', name='feedbacktypes'), nullable=False),
    sa.ForeignKeyConstraint(['registration_id'], ['registration.registration_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('feedbacks')
    # ### end Alembic commands ###

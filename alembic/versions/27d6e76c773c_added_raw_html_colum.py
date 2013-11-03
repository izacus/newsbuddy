"""Added raw_html column to article table

Revision ID: 27d6e76c773c
Revises: 3095c2d804d
Create Date: 2013-11-03 13:51:05.936779

"""

# revision identifiers, used by Alembic.
revision = '27d6e76c773c'
down_revision = '3095c2d804d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('news', sa.Column('raw_html', sa.UnicodeText))


def downgrade():
    op.drop_column('news', 'raw_html')

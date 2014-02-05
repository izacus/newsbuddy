"""Added tags table

Revision ID: 42b486977799
Revises: 27d6e76c773c
Create Date: 2014-02-05 23:57:37.029556

"""

# revision identifiers, used by Alembic.
revision = '42b486977799'
down_revision = '27d6e76c773c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('tags',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('tag_name', sa.UnicodeText, nullable=False))
    op.create_table('news_tags',
                    sa.Column('tag_id', sa.Integer, sa.ForeignKey('tags.id')),
                    sa.Column('news_id', sa.String, sa.ForeignKey('news.id')))
    op.create_index('tags_name', 'tags', ['tag_name'])


def downgrade():
    op.drop_index('tags_name')
    op.drop_table('news_tags')
    op.drop_table('tags')

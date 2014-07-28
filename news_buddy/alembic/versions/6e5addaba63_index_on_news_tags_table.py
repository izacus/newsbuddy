"""Index on news_tags table

Revision ID: 6e5addaba63
Revises: 42b486977799
Create Date: 2014-07-28 14:19:47.649154

"""

# revision identifiers, used by Alembic.
revision = '6e5addaba63'
down_revision = '42b486977799'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column("news", "id", type_=sa.types.CHAR(length=128))
    op.alter_column("news_tags", "news_id", type_=sa.types.CHAR(length=128))
    op.create_index("news_tags_news_idx", "news_tags", ["news_id"])
    op.create_index("news_tags_tags_idx", "news_tags", ["tag_id"])
    op.execute("CREATE UNIQUE INDEX news_tags_pair_idx ON news_tags (news_id, tag_id)")

def downgrade():
    op.drop_constraint("news_tags_pair_uq", "news_tags")
    op.drop_index("news_tags_news_idx")
    op.drop_index("news_tags_tags_idx")
    op.drop_index("news_tags_pair_idx")

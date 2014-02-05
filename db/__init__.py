from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os
import settings

Base = declarative_base()
db_engine = create_engine(settings.DB_CONNECTION_STRING)

def check_create_db():
    if not db_engine.dialect.has_table(db_engine.connect(), 'news'):
        from db.news import Base, NewsItem
        Base.metadata.create_all(db_engine)
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config(os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")), "alembic.ini"))
        command.stamp(alembic_cfg, "head")

Session = scoped_session(sessionmaker(bind=db_engine))
check_create_db()

def get_db_session():
    return Session()


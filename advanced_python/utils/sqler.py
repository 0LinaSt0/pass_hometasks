from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from utils.config import DATABASE_URL



engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False,
    bind=engine
)
Base = declarative_base()


class Photo(Base):
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
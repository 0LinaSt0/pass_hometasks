from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

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
    filepath = Column(String, index=True)
    about = Column(String, index=True)

    face_encodings = relationship(
        'FaceEncodings', 
        back_populates='photos',
        cascade='all, delete-orphan'
    )



class FaceEncodings(Base):
    '''
    If there are some faces on one photo, where are added
    every finded face as new row. So, one photo can have
    more than one face_encodings.
    '''
    __tablename__ = 'face_encodings'

    id = Column(Integer, primary_key=True, index=True)
    photo_id = Column(Integer, ForeignKey('photo.id'), nullable=False)
    encoding = Column(ARRAY(float), nullable=False)

    photo = relationship('Photo', back_populates='face_encodings')



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)

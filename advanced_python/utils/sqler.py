from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey
)
from sqlalchemy import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from utils.config import DATABASE_URL

from utils.logging import LoggingMethods

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base = declarative_base()


# ~~~~~~~~~~~~ Photos datatables ~~~~~~~~~~~~

class Photo(LoggingMethods, Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    filepath = Column(String, index=True)


class PhotoDatabase(Photo):
    __tablename__ = 'photos'

    about = Column(String, index=True)

    face_encodings = relationship(
        'FaceEncodingsDatabase',
        back_populates='photo',
        cascade='all, delete-orphan'
    )

    def __init__(self, **kwargs):
        # Filter out any extra keys that are not defined in the class
        valid_keys = {'id', 'filename', 'filepath', 'about'}
        for key, value in kwargs.items():
            if key in valid_keys:
                setattr(self, key, value)


class PhotoTmp(Photo):
    __tablename__ = 'tmp_photos'

    face_encodings = relationship(
        'FaceEncodingsTmp',
        back_populates='tmp_photo',
        cascade='all, delete-orphan'
    )

    def __init__(self, **kwargs):
        # Filter out any extra keys that are not defined in the class
        valid_keys = {'id', 'filename', 'filepath'}
        for key, value in kwargs.items():
            if key in valid_keys:
                setattr(self, key, value)


# ~~~~~~~~~~~~ Encoding datatables ~~~~~~~~~~~~

class FaceEncodings(LoggingMethods, Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    encoding = Column(JSON, nullable=False)


class FaceEncodingsDatabase(FaceEncodings):
    __tablename__ = 'face_encodings_database'

    photo_id = Column(Integer, ForeignKey('photos.id'))

    photo = relationship(
        'PhotoDatabase',
        back_populates='face_encodings'
    )


class FaceEncodingsTmp(FaceEncodings):
    __tablename__ = 'face_encodings_tmp'

    photo_id = Column(Integer, ForeignKey('tmp_photos.id'))

    tmp_photo = relationship(
        'PhotoTmp',
        back_populates='face_encodings'
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)

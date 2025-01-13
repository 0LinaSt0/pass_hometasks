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
        back_populates='photo',
        cascade='all, delete-orphan'
    )

class TmpPhoto(Base):
    __tablename__ = 'tmp_photos'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    filepath = Column(String, index=True)

class FaceEncodings(Base):
    __tablename__ = 'face_encodings'

    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys for both Photo and TmpPhoto
    photo_id = Column(Integer, ForeignKey('photos.id'), nullable=True)  # Nullable for polymorphic behavior
    tmp_photo_id = Column(Integer, ForeignKey('tmp_photos.id'), nullable=True)  # Nullable for polymorphic behavior
    photo_type = Column(String(50), nullable=False)  # 'photo' or 'tmp_photo'
    
    encoding = Column(JSON, nullable=False)

    # Define relationships for both types of photos
    photo = relationship(
        "Photo",
        primaryjoin="and_(FaceEncodings.photo_id==Photo.id, FaceEncodings.photo_type=='photo')",
        back_populates='face_encodings'
    )
    
    tmp_photo = relationship(
        "TmpPhoto",
        primaryjoin="and_(FaceEncodings.tmp_photo_id==TmpPhoto.id, FaceEncodings.photo_type=='tmp_photo')"
    )

    @property
    def actual_photo(self):
        if self.photo_type == 'photo':
            return self.photo
        elif self.photo_type == 'tmp_photo':
            return self.tmp_photo
        return None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)

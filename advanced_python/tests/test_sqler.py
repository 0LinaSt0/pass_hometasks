import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Adjust import as necessary
from utils.sqler import (
    Base, 
    PhotoDatabase, 
    PhotoTmp, 
    FaceEncodingsDatabase, 
    FaceEncodingsTmp, 
    get_db
)

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


@pytest.fixture(scope='module')
def setup_database():
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(setup_database):
    # Create a new session for each test
    db = SessionLocal()
    yield db
    db.close()


def test_create_photo(db_session):
    photo = PhotoDatabase(filename='test_image.jpg',
                          filepath='/images/', about='Test image')
    db_session.add(photo)
    db_session.commit()

    assert photo.id is not None  # The ID should be auto-generated
    assert photo.filename == 'test_image.jpg'
    assert photo.about == 'Test image'


def test_read_photo(db_session):
    photo = db_session.query(PhotoDatabase).filter_by(
        filename='test_image.jpg').first()

    assert photo is not None
    assert photo.filepath == '/images/'


def test_update_photo(db_session):
    photo = db_session.query(PhotoDatabase).filter_by(
        filename='test_image.jpg').first()

    # Update the photo's about field
    photo.about = 'Updated test image'
    db_session.commit()

    updated_photo = db_session.query(
        PhotoDatabase).filter_by(id=photo.id).first()

    assert updated_photo.about == 'Updated test image'


def test_delete_photo(db_session):
    photo = db_session.query(PhotoDatabase).filter_by(
        filename='test_image.jpg').first()

    db_session.delete(photo)
    db_session.commit()

    deleted_photo = db_session.query(
        PhotoDatabase).filter_by(id=photo.id).first()

    assert deleted_photo is None  # The photo should be deleted


def test_create_face_encoding(db_session):
    photo = PhotoDatabase(filename='test_image.jpg',
                          filepath='/images/', about='Test image')
    db_session.add(photo)

    face_encoding = FaceEncodingsDatabase(
        encoding={"face": [0.1, 0.2, 0.3]}, photo=photo)

    db_session.add(face_encoding)
    db_session.commit()

    assert face_encoding.id is not None

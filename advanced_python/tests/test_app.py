import pytest
from unittest import mock
from unittest.mock import AsyncMock, MagicMock
from fastapi import UploadFile
from sqlalchemy.orm import Session

from utils.pydantic_validation import PhotoUpload

from app.utils import (
    file_uploader,
    database_updater,
    save_tmp_photo_info,
    process_image,
    PhotoDatabase,
    FaceEncodingsDatabase,
    PhotoTmp,
)


@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def mock_upload_file():
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.filename = "test_image.jpg"
    mock_file.read.return_value = b"fake_image_data"
    return mock_file


@pytest.mark.asyncio
async def test_file_uploader(mock_upload_file):
    main_filepath = "/tmp/"

    valid_data = await file_uploader(main_filepath, file=mock_upload_file)

    assert valid_data.filename == "test_image.jpg"
    assert valid_data.filepath == f"{main_filepath}test_image.jpg"


@pytest.mark.asyncio
@mock.patch('app.utils.log_update_db', new_callable=AsyncMock)
async def test_database_updater(mock_log_update_db, mock_db_session):
    valid_data = PhotoUpload(
        filename="test_image.jpg",
        main_filepath="/tmp/",
        about="Test image"
    )

    # Mocking PhotoDatabase and FaceEncodingsDatabase
    photo_datatable = PhotoDatabase
    encoding_datatable = FaceEncodingsDatabase

    with mock.patch('app.utils.FaceDetection.get_face_encoding_by_img_path', return_value=[]) as mock_img, \
        mock.patch('app.utils.encoding_from_json', return_value=["0.1;0.2;0.3"]) as mock_encoded:
        new_photo = await database_updater(valid_data, photo_datatable, encoding_datatable, mock_db_session)

    assert new_photo.filename == "test_image.jpg"


@pytest.mark.asyncio
async def test_save_tmp_photo_info(mock_upload_file, mock_db_session):
    # Mocking the behavior of file_uploader and database_updater
    with mock.patch('app.utils.file_uploader', return_value=PhotoTmp(filename="temp_image.jpg", filepath="/tmp/temp_image.jpg")) as mock_uploader:
        with mock.patch('app.utils.database_updater', return_value=PhotoTmp(id=1)) as mock_updater:
            new_tmp_photo_id = await save_tmp_photo_info(mock_upload_file, mock_db_session)

            assert new_tmp_photo_id == 1  # Check if the returned ID is correct


@pytest.mark.asyncio
async def test_process_image(mock_db_session):
    # Mocking the behavior of FaceEncodingsDatabase and FaceComparator
    encoding_table = FaceEncodingsDatabase

    # Mocking the database query results
    mock_db_session.query.return_value.filter.return_value.with_entities.return_value.all.return_value = [
        MagicMock(encoding={"face": [0.1, 0.2, 0.3]}),
        MagicMock(encoding={"face": [0.3, 0.2, 0.1]})
    ]

    # Assuming you have a method to get face encodings from the database
    results = await process_image(image_id=1, encoding_table=encoding_table, db=mock_db_session)

    assert isinstance(results, list)  # Ensure results are returned as a list

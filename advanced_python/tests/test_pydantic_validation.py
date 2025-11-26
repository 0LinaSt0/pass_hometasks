import pytest
from pydantic import ValidationError

from utils.pydantic_validation import PhotoUpload




class TestPhotoUpload:
    def test_check_filename_empty(self):
        with pytest.raises(ValidationError):
            PhotoUpload(filename='', main_filepath='some/path')


    def test_check_filename_invalid_chars(self):
        photo = PhotoUpload(
            filename='مرحبًا@_фото.phg',
            main_filepath='some/path'
        )

        assert photo.filename == 'mrHban@_foto.phg'


    def test_serialize_model(self):
        photo = PhotoUpload(filename='My Photo.jpg', main_filepath='/images/')
        
        serialized = photo.serialize_model(lambda x: x.dict())
        
        assert serialized['filename'] == 'My_Photo.jpg'
        assert serialized['filepath'] == '/images/My_Photo.jpg'

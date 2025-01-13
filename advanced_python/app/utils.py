from typing import Union

from fastapi import UploadFile, File, Form

from sqlalchemy.orm import Session

from face_comparator.utils import encoding_to_json
from face_comparator.face_detector import FaceDetection

from utils.pydantic_validation import PhotoUpload
from utils.sqler import (
    Photo,
    TmpPhoto,
    FaceEncodings
)



async def file_uploader(
    file: UploadFile = File(...),
    **kwargs
):
    valid_data = PhotoUpload(filename=file.filename, **kwargs)

    with open(valid_data.filepath, 'wb') as f:
        content = await file.read()
        f.write(content)

    return valid_data


async def database_updater(
    valid_data: PhotoUpload, 
    datatable: Union[Photo, TmpPhoto],
    db: Session
):

    new_photo = datatable(
        filename=valid_data.filename, 
        filepath=valid_data.filepath,
        about=valid_data.about
    )

    db.add(new_photo)
    db.commit()


    photo_encodings = encoding_to_json(
        FaceDetection.get_face_encoding_by_img_path(
            new_photo.filepath
        )
    )

    for photo_encoding in photo_encodings:
        encoding = FaceEncodings(
            photo_id=new_photo.id,
            photo_type='photo',
            encoding=photo_encoding
        )
        db.add(encoding)
        db.commit()

    return new_photo
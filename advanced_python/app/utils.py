from typing import Union

from fastapi import UploadFile, File

from sqlalchemy.orm import Session

from face_comparator.utils import encoding_to_json
from face_comparator.face_detector import FaceDetection

from utils.pydantic_validation import PhotoUpload
from utils.sqler import (
    PhotoDatabase,
    PhotoTmp,
    FaceEncodingsDatabase,
    FaceEncodingsTmp,
)

from utils.config import PATH_TMP_PICTURES


async def file_uploader(
    main_filepath: str,
    file: UploadFile = File(...),
    **kwargs
):
    valid_data = PhotoUpload(
        filename=file.filename, main_filepath=main_filepath, **kwargs
    )

    with open(valid_data.filepath, 'wb') as f:
        content = await file.read()
        f.write(content)

    return valid_data


async def database_updater(
    valid_data: PhotoUpload,
    photo_datatable: Union[PhotoDatabase, PhotoTmp],
    encoding_datatable: Union[FaceEncodingsDatabase, FaceEncodingsTmp],
    db: Session
):

    data = valid_data.model_dump()

    data_for_datatable = {
        field: value for field, value in data.items()
    }

    new_photo = photo_datatable(**data_for_datatable)

    db.add(new_photo)
    db.commit()

    photo_encodings = encoding_to_json(
        FaceDetection.get_face_encoding_by_img_path(
            new_photo.filepath
        )
    )

    for photo_encoding in photo_encodings:
        encoding = encoding_datatable(
            photo_id=new_photo.id,
            encoding=photo_encoding
        )
        db.add(encoding)
        db.commit()

    return new_photo


async def save_tmp_photo_info(
    image: UploadFile,
    db: Session
):
    valid_data = await file_uploader(
        main_filepath=PATH_TMP_PICTURES, file=image
    )

    new_tmp_photo = await database_updater(
        valid_data=valid_data,
        photo_datatable=PhotoTmp,
        encoding_datatable=FaceEncodingsTmp,
        db=db
    )

    return new_tmp_photo.id


async def process_image(
    image_id: str,
    image_type: str,
    db: Session
):
    # TODO: Realize preprocess_image
    import asyncio
    await asyncio.sleep(3)

    # all_encodings = db.query(FaceEncodings).all()

    # for record in all_encodings:
    #     print(record)
    #     print(record.id)

    print(f"Processed image with ID: {image_id} and type {image_type}")

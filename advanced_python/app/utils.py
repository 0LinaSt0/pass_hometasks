import bisect
from typing import Union

from fastapi import UploadFile, File

from sqlalchemy.orm import Session

from face_comparator.utils import encoding_to_json, encoding_from_json
from face_comparator.face_detector import FaceDetection, FaceComparator

from utils.pydantic_validation import PhotoUpload
from utils.sqler import (
    PhotoDatabase,
    PhotoTmp,
    FaceEncodingsDatabase,
    FaceEncodingsTmp,
)

from utils.config import PATH_TMP_PICTURES, BASE_DIR


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
) -> int:
    valid_data = await file_uploader(
        main_filepath=BASE_DIR+PATH_TMP_PICTURES, file=image
    )

    new_tmp_photo = await database_updater(
        valid_data=valid_data,
        photo_datatable=PhotoTmp,
        encoding_datatable=FaceEncodingsTmp,
        db=db
    )

    return new_tmp_photo.id


async def process_image(
    image_id: int,
    image_table: Union[PhotoDatabase, PhotoTmp],
    encoding_table: Union[FaceEncodingsDatabase, FaceEncodingsTmp],
    db: Session
):
    same_faces_idxs = []
    
    photo_encoding_mtxs = db.query(encoding_table).filter(
        encoding_table.photo_id == image_id
    ).with_entities(
        encoding_table.encoding
    ).all()

    if encoding_table == FaceEncodingsDatabase:
        all_db_encodings = db.query(FaceEncodingsDatabase)\
            .filter(FaceEncodingsDatabase.photo_id != image_id)\
            .all()
    else:
        all_db_encodings = db.query(FaceEncodingsDatabase).all()

    for record in all_db_encodings:
        for photo_encoding_mtx in photo_encoding_mtxs:
            photo_encoding_mtx = encoding_from_json(
                photo_encoding_mtx.encoding
            )
            photo_database_mtx = encoding_from_json(
                record.encoding
            )
            
            dist, is_same = FaceComparator.faces_euclidean_distance(
                photo_database_mtx,
                photo_encoding_mtx
            )
            
            if is_same:
                bisect.insort(
                    same_faces_idxs,
                    (dist, is_same, record.photo_id)
                )

    return same_faces_idxs

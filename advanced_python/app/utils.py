import bisect
from typing import Union, List, Tuple

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
from utils.logging import log_raises, log_update_db


@log_raises
async def file_uploader(
    main_filepath: str,
    file: UploadFile = File(...),
    **kwargs
) -> PhotoUpload:
    """Save photo as file

    Parameters
    ----------
    main_filepath : str
        main filepath for saving
    file : UploadFile, optional
        photo for saving, by default File(...)

    Returns
    -------
    PhotoUpload
        saved photo
    """
    valid_data = PhotoUpload(
        filename=file.filename, main_filepath=main_filepath, **kwargs
    )

    with open(valid_data.filepath, 'wb') as f:
        content = await file.read()
        f.write(content)

    return valid_data


@log_raises
@log_update_db
async def database_updater(
    valid_data: PhotoUpload,
    photo_datatable: Union[PhotoDatabase, PhotoTmp],
    encoding_datatable: Union[FaceEncodingsDatabase, FaceEncodingsTmp],
    db: Session
) -> Union[PhotoDatabase, PhotoTmp]:
    """Add new photo one of the database

    Parameters
    ----------
    valid_data : PhotoUpload
        photo for uploading
    photo_datatable : Union[PhotoDatabase, PhotoTmp]
        table for uploading
    encoding_datatable : Union[FaceEncodingsDatabase, FaceEncodingsTmp]
        table for save embeddings
    db : Session
        database

    Returns
    -------
    Union[PhotoDatabase, PhotoTmp]
        uploaded photo
    """
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


@log_raises
async def save_tmp_photo_info(
    image: UploadFile,
    db: Session
) -> int:
    """Save temporary photo

    Parameters
    ----------
    image : UploadFile
        image for uploading
    db : Session
        database

    Returns
    -------
    int
        id of new tmp photo
    """
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


@log_raises
async def process_image(
    image_id: int,
    encoding_table: Union[FaceEncodingsDatabase, FaceEncodingsTmp],
    db: Session
) -> List[Tuple[float, bool, int]]:
    """Find the same pictures from database

    Parameters
    ----------
    image_id : int
        id to reference image
    encoding_table : Union[FaceEncodingsDatabase, FaceEncodingsTmp]
        one of the table with embeddings
    db : Session
        database

    Returns
    -------
    List[Tuple[float, bool, int]], sorted
        list with dist, is_same, record.photo_id
        sorted by dist
    """
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

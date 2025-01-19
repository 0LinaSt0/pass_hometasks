from fastapi.responses import RedirectResponse
import os

from fastapi import (
    FastAPI,
    Request,
    UploadFile,
    File,
    Depends,
    Form
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from app.utils import (
    file_uploader,
    database_updater,
    process_image,
    save_tmp_photo_info
)

from utils.config import (
    DIR_TEMPLATES,
    HTML_TEMPLATES,
    PATH_PICTURES,
    BASE_DIR
)
from utils.sqler import (
    FaceEncodingsDatabase,
    FaceEncodingsTmp,
    PhotoDatabase,
    PhotoTmp,
    get_db
)


app = FastAPI()
templates = Jinja2Templates(directory=DIR_TEMPLATES)

app.mount('/pictures', StaticFiles(directory=BASE_DIR), name='static')


@app.get('/', response_class=HTMLResponse)
async def read_root(
    request: Request,
    db: Session = Depends(get_db)
):
    photos = db.query(PhotoDatabase).all()

    table_content = templates.TemplateResponse(
        HTML_TEMPLATES['imges_table'],
        {
            'request': request,
            'photos': photos,
            'path_pictures': PATH_PICTURES
        }
    ).body.decode()

    delete_content = templates.TemplateResponse(
        HTML_TEMPLATES['delete'],
        {'request': request}
    ).body.decode()

    return templates.TemplateResponse(
        HTML_TEMPLATES['root'],
        {
            'request': request,
            'table_content': table_content,
            'delete_content': delete_content,
        }
    )


@app.post("/wait")
async def waiting_comparation(
    image: UploadFile = File(None),
    image_id: int = Form(None),
    db: Session = Depends(get_db),
):
    image_type = PhotoDatabase

    if image:
        image_id = await save_tmp_photo_info(image, db)
        image_type = PhotoTmp

    await process_image(image_id, image_type, db)
    return RedirectResponse(f'/result?image_id={image_id}', status_code=303)


@app.get("/result")
async def get_result(
    image_id: int,
    request: Request
):
    # TODO: To do result comparation
    # Replace with actual result fetching logic
    result = f"Comparison Result: {image_id}"
    return templates.TemplateResponse("comparation_result.html", {"result": result, 'request': request})


@app.post('/upload')
async def upload_picture(
    image: UploadFile = File(...),
    about: str = Form(None),
    db: Session = Depends(get_db)
):
    valid_data = await file_uploader(
        main_filepath=PATH_PICTURES, file=image, about=about
    )

    await database_updater(
        valid_data=valid_data,
        photo_datatable=PhotoDatabase,
        encoding_datatable=FaceEncodingsDatabase,
        db=db
    )

    return RedirectResponse(url='/', status_code=303)


@app.post('/delete-image')
def delete_image(
    image_id: int = Form(...),
    db: Session = Depends(get_db)
):
    image = db.query(PhotoDatabase).filter(
        PhotoDatabase.id == image_id).first()

    if not image:
        return {"status": "error", "message": "Фото с таким id не найдено!"}

    if os.path.exists(filepath := (BASE_DIR + image.filepath)):
        os.remove(filepath)

    db.delete(image)
    db.commit()

    return {"status": "success", "message": "Фото успешно удалено"}

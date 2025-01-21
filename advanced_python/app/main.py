import os
from typing import Union

from fastapi.responses import RedirectResponse

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
from starlette.middleware.sessions import SessionMiddleware

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
    BASE_DIR,
    SECRET_KEY
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

app.mount(
    '/pictures', 
    StaticFiles(directory=os.path.join(BASE_DIR, PATH_PICTURES)),
    name='static'
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)



@app.get('/', response_class=HTMLResponse)
async def read_root(
    request: Request,
    db: Session = Depends(get_db)
):
    photos = db.query(PhotoDatabase).all()

    delete_content = templates.TemplateResponse(
        HTML_TEMPLATES['delete'],
        {'request': request}
    ).body.decode()

    return templates.TemplateResponse(
        HTML_TEMPLATES['root'],
        {
            'request': request,
            'photos': photos,
            'delete_content': delete_content,
        }
    )


@app.post('/wait')
async def waiting_comparation(
    request: Request,
    image: UploadFile = File(None),
    image_id: int = Form(None),
    db: Session = Depends(get_db),
):
    image_table = PhotoDatabase
    encoding_table = FaceEncodingsDatabase
    refer_folder = ''

    if image:
        image_id = await save_tmp_photo_info(image, db)
        image_table = PhotoTmp
        encoding_table = FaceEncodingsTmp
        refer_folder = 'temprorary_photos/'

    same_faces = await process_image(
        image_id, image_table, encoding_table, db
    )
    request.session['same_faces'] = same_faces
    request.session['refer_filepath'] = \
        refer_folder\
        + db.query(image_table).filter(
            image_table.id == image_id
        ).first().filename
    return RedirectResponse(f'/result?refer_photo_id={image_id}', status_code=303)


@app.get('/result')
async def get_result(
    refer_photo_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    same_faces = request.session.get('same_faces')
    refer_filepath = request.session.get('refer_filepath')

    print(refer_filepath)

    photos = db.query(PhotoDatabase).filter(
        PhotoDatabase.id.in_([el[2] for el in same_faces])
    ).all()

    return templates.TemplateResponse('comparation_result.html', {
        'refer_photo_filepath': refer_filepath,
        'photos': photos,
        'request': request
    })


@app.post('/upload')
async def upload_picture(
    image: UploadFile = File(...),
    about: str = Form(None),
    db: Session = Depends(get_db)
):
    valid_data = await file_uploader(
        main_filepath=BASE_DIR + PATH_PICTURES, file=image, about=about
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
        return {'status': 'error', 'message': 'Фото с таким id не найдено!'}

    if os.path.exists(filepath := (BASE_DIR + image.filepath)):
        os.remove(filepath)

    db.delete(image)
    db.commit()

    return {'status': 'success', 'message': 'Фото успешно удалено'}

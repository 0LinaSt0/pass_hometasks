import os

from fastapi import (
    FastAPI,
    Request,
    UploadFile,
    BackgroundTasks,
    File,
    Depends,
    Form
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from app.utils import file_uploader, database_updater

from utils.config import (
    DIR_TEMPLATES, 
    HTML_TEMPLATES, 
    PATH_PICTURES, 
    PATH_TMP_PICTURES,
    BASE_DIR
)
from utils.pydantic_validation import PhotoUpload
from utils.sqler import (
    Photo,
    FaceEncodings,
    TmpPhoto,
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
    photos = db.query(Photo).all()

    table_content = templates.TemplateResponse(
        HTML_TEMPLATES['imges_table'],
        {
            'request': request,
            'photos': photos,
            'path_pictures': PATH_PICTURES
        }
    ).body.decode()

    delete_content = templates.TemplateResponse(\
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

@app.post("/wait/")
async def waiting_comparation(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    image_id: int = Form(...),
    db: Session = Depends(get_db)
):
    if image:
        async def save_tmp_photo_info(image: UploadFile):
            valid_data = await file_uploader(image)

            new_tmp_photo = await database_updater(valid_data, Photo, db)

            return new_tmp_photo.id
    
        image_id = background_tasks.add_task(save_tmp_photo_info, image)
    
    # Define process_image function
    async def process_image(image_id: int):
        # TODO: process_image
        ...

    background_tasks.add_task(process_image, image_id)
    return templates.TemplateResponse("waiting.html", {"request": Request})


@app.get("/result/")
async def get_result():
    # This should ideally check if the processing is complete and return results.
    
    # TODO: To do result comparation
    result = "Comparison Result"  # Replace with actual result fetching logic
    return templates.TemplateResponse("comparation_result.html", {"request": Request, "result": result})



@app.post('/upload/')
async def upload_picture(
    file: UploadFile = File(...),
    about: str = Form(None),
    db: Session = Depends(get_db)
):
    valid_data = await file_uploader(file, about=about)

    await database_updater(valid_data, Photo, db)

    return RedirectResponse(url='/', status_code=303)



@app.post('/compare/')
async def photo_comparations(
    selected_photo: int = Form(...), 
    db: Session = Depends(get_db)
):
    # TODO: REALIZE LOGIC WITH COMPARATION PHOTOS
    return {'selected_photo': selected_photo}



@app.post('/delete-image/')
def delete_image(
    image_id: int = Form(...),
    db: Session = Depends(get_db)
):
    image = db.query(Photo).filter(Photo.id == image_id).first()

    if not image:
        return {"status": "error", "message": "Фото с таким id не найдено!"}

    if os.path.exists(filepath := (BASE_DIR + image.filepath)):
        os.remove(filepath)

    
    db.delete(image)
    db.commit()

    return {"status": "success", "message": "Фото успешно удалено"}
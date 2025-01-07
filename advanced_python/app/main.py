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

from utils.config import (
    DIR_TEMPLATES, 
    HTML_TEMPLATES, 
    PATH_PICTURES, 
    BASE_DIR
)
from utils.sqler import Photo, get_db


app = FastAPI()
templates = Jinja2Templates(directory=DIR_TEMPLATES)

app.mount('/pictures', StaticFiles(directory=BASE_DIR), name='static')


@app.get('/', response_class=HTMLResponse)
async def read_root(
    request: Request,
    db: Session = Depends(get_db)
):
    photos = db.query(Photo).all()

    table_content = templates.TemplateResponse("table_template.html", {
        "request": request,
        'photos': photos,
        'path_pictures': PATH_PICTURES
    }).body.decode()

    return templates.TemplateResponse(
        HTML_TEMPLATES['root'],
        {
            'request': request,
            'table_content': table_content
    })


@app.post('/upload/')
async def upload_picture(
    file: UploadFile = File(...),
    about: str = Form(None),
    db: Session = Depends(get_db)
):
    filepath = PATH_PICTURES + file.filename

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    new_photo = Photo(filename=file.filename, about=about)
    db.add(new_photo)
    db.commit()
    return RedirectResponse(url='/', status_code=303)



@app.post("/find/")
async def find_comparations(
    selected_photo: int = Form(...), 
    db: Session = Depends(get_db)
):
    # TODO: REALIZE LOGIC WITH COMPARATION PHOTOS
    return {'selected_photo': selected_photo}
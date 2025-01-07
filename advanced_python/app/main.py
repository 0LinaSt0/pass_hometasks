from fastapi import FastAPI, Request, File, UploadFile, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from utils.config import DIR_TEMPLATES, HTML_TEMPLATES, PATH_PICTURES, BASE_DIR
from utils.sqler import Photo, get_db


app = FastAPI()
templates = Jinja2Templates(directory=DIR_TEMPLATES)

app.mount(BASE_DIR, StaticFiles(directory=BASE_DIR), name='static')


@app.get('/', response_class=HTMLResponse)
async def read_root(
    request: Request,
    db: Session = Depends(get_db)
):
    photos = db.query(Photo).all()
    return templates.TemplateResponse(
        HTML_TEMPLATES['root'], 
        {
            'request': request, 
            'photos': photos, 
            'path_pictures': PATH_PICTURES
    })


@app.post('/upload/')
async def upload_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filepath = PATH_PICTURES + file.filename

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    new_photo = Photo(filename=file.filename)
    db.add(new_photo)
    db.commit()
    return {"filename": file.filename}
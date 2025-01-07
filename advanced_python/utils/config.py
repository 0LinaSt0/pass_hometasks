import os



BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


DIR_TEMPLATES = 'materials/templates/'

HTML_TEMPLATES = {
    'root': 'index.html',
    'upload': ''
}

PATH_PICTURES = 'materials/pictures/'


DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'materials', 'db', 'photos.db')}"
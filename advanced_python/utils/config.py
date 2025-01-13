import os



BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


DIR_TEMPLATES = 'materials/templates/'

HTML_TEMPLATES = {
    'root': 'index.html',
    'imges_table': 'table_template.html',
    'delete': 'delete.html'
}

PATH_PICTURES = 'materials/pictures/'
PATH_TMP_PICTURES = 'materials/pictures/temprorary_photos/'


DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'materials', 'db', 'face_comparator.db')}"
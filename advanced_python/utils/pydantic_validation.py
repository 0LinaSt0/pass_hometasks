from deep_translator import GoogleTranslator

from pydantic import BaseModel, field_validator
from utils.config import PATH_PICTURES


class PhotoUpload(BaseModel):
    filename: str
    about: str | None


    @field_validator('filename')
    def check_filename(cls, value):
        i_extention = value.rfind('.')
        main_filename = value[:i_extention]
        extention_filename = value[i_extention:]

        translated_filename = GoogleTranslator(
            source='auto', target='en'
        ).translate(main_filename)

        translated_filename = translated_filename.replace(' ', '_')

        new_value = translated_filename + extention_filename

        return new_value


    @property
    def filepath(self):
        return PATH_PICTURES + self.filename
    


if __name__ == '__main__':
    filename = 'красивый медведь.хахаха .png'
    about = 'AAAAAAA'

    value = PhotoUpload(filename=filename, about=about)

    print(value.filename, value.about)
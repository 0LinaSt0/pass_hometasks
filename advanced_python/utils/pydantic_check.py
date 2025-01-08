from deep_translator import GoogleTranslator

from pydantic import BaseModel, field_validator


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
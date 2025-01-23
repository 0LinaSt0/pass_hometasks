from deep_translator import GoogleTranslator

from pydantic import BaseModel, field_validator, model_serializer

from utils.logging import LoggingMethods


class PhotoUpload(LoggingMethods, BaseModel):
    filename: str
    main_filepath: str
    about: str | None = None

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
    def filepath(self) -> str:
        return self.main_filepath + self.filename

    @model_serializer(mode='wrap')
    def serialize_model(self, handler) -> dict:
        result = handler(self)
        result['filepath'] = self.filepath
        return result

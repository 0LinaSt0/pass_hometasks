from unidecode import unidecode

from pydantic import BaseModel, field_validator, model_serializer

from utils.logging import LoggingMethods


class PhotoUpload(LoggingMethods, BaseModel):
    filename: str
    main_filepath: str
    about: str | None = None

    @field_validator('filename')
    def check_filename(cls, value):
        i_extention = value.rfind('.')
        if i_extention == -1:
            raise ValueError('Filename must include extention')
        main_filename = value[:i_extention]
        extention_filename = value[i_extention:]

        try:
            unidecode_filename = unidecode(
                main_filename
            )
        except:
            unidecode_filename = main_filename

        unidecode_filename = unidecode_filename.replace(' ', '_')

        new_value = unidecode_filename + extention_filename

        return new_value

    @property
    def filepath(self) -> str:
        return self.main_filepath + self.filename

    @model_serializer(mode='wrap')
    def serialize_model(self, handler) -> dict:
        result = handler(self)
        result['filepath'] = self.filepath
        return result

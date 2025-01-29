import logging
from functools import wraps
from fastapi import HTTPException
from utils.config import LOG_FILEPATH


logging.basicConfig(
    filename=LOG_FILEPATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def log_road(func):
    """Redirect to road logging

    Parameters
    ----------
    func : 
        road function
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f'Redirect to {func.__name__} road function')
        result = await func(*args, **kwargs)

        return result
    return wrapper


def log_raises(func):
    """Logging raises

    Parameters
    ----------
    func : 
        any execute function

    Raises
    ------
    HTTPException
        re-raser of func raise
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(
                f'Raise during {func.__name__} function execution: {e}'
            )
            raise HTTPException(
                status_code=500,
                detail=f'Server error: {e}\nLook to {LOG_FILEPATH} for details'
            )
    return wrapper


def log_raises_not_async(func):
    """Logging raises

    Parameters
    ----------
    func : 
        any execute function

    Raises
    ------
    HTTPException
        re-raser of func raise
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(
                f'Raise during {func.__name__} function execution: {e}'
            )
            raise HTTPException(
                status_code=500,
                detail=f'Server error: {e}\nLook to {LOG_FILEPATH} for details'
            )
    return wrapper


def log_update_db(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        logger.info(
            f'The table {kwargs["photo_datatable"]} was updated'
        )

        return result

    return wrapper


class LoggingMethods:
    """Class for logging all child method by log_raises
    """
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for attr, value in cls.__dict__.items():
            if callable(value):
                setattr(cls, attr, log_raises_not_async(value))

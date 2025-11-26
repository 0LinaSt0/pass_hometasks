# decorators.py

import logging
from functools import wraps
from fastapi import HTTPException
from typing import Callable  # Импортируем Callable

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_execution(func):
    """Декоратор для логирования начала и конца выполнения функции"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"Начало выполнения функции: {func.__name__}")
        result = await func(*args, **kwargs)
        logger.info(f"Конец выполнения функции: {func.__name__}")
        return result
    return wrapper

def observe_errors(func):
    """Декоратор для отслеживания ошибок и логирования их"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка при выполнении функции {func.__name__}: {e}")
            raise HTTPException(status_code=500, detail="Произошла ошибка сервера")
    return wrapper

def cache_decorator(func: Callable):
    """Простой декоратор для кэширования результата асинхронной функции"""
    cache = {}

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Генерация ключа для кэша, чтобы использовать args и kwargs
        key = (args, tuple(kwargs.items()))
        if key in cache:
            logger.info("Возвращаем результат из кэша")
            return cache[key]
        
        # Выполнение функции и кэширование результата
        result = await func(*args, **kwargs)
        cache[key] = result
        logger.info(f"Результат сохранен в кэш: {key}")
        return result

    return wrapper

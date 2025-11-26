# app.py

from fastapi import FastAPI
from decorators import log_execution, observe_errors, cache_decorator

app = FastAPI()

@app.get("/add/{x}/{y}")
@log_execution
async def add(x: int, y: int):
    """Эндпоинт для сложения двух чисел"""
    return {"result": x + y}

@app.get("/divide/{x}/{y}")
@observe_errors
async def divide(x: int, y: int):
    """Эндпоинт для деления с обработкой ошибок"""
    return {"result": x / y}

@app.get("/cached_square/{x}")
@cache_decorator
async def cached_square(x: int):
    """Эндпоинт для вычисления квадрата числа с кэшированием"""
    return {"result": x ** 2}

# uvicorn app:app --reload
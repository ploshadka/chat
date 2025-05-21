import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Лог SQL-запросов (в dev можно True)
    future=True  # Совместимость с SQLAlchemy 2.x синтаксисом
)

# Настраиваем сессионный класс (фабрику) для работы с БД
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Позволяет использовать объект после commit() без повторного запроса
    autoflush=False  # flush() вызывается вручную → исключает неожиданные запросы
)

# Базовый класс для всех моделей
Base = declarative_base()


# Для Depends
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


# Асинхронный контекстный менеджер для ручного получения сессии (вне Depends)
@asynccontextmanager
async def get_session_with_context():
    async with SessionLocal() as session:
        yield session

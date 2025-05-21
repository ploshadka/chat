import os
import pytest
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator


# Загружаем переменные окружения ОДИН РАЗ для всех тестов
@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv(dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env.dev")))


# Создаём свою engine и session - не лезим в bd.py
@pytest.fixture
async def test_db_session() -> AsyncGenerator[AsyncSession, None]:
    # Будет установлен после load_env
    from app.config.db import DATABASE_URL
    engine = create_async_engine(DATABASE_URL, echo=False, future=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

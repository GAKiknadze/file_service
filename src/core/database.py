from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


engine: AsyncEngine


async def init_engine(uri: str) -> None:
    """Инициализация AsyncEngine"""
    global engine
    engine = create_async_engine(uri, future=True)


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии базы данных"""
    global engine  # noqa: F824
    local_session = async_sessionmaker(
        engine,
        autocommit=False,
        autoflush=True,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with local_session() as session:
        yield session
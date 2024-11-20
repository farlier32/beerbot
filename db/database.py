from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+asyncpg://postgres:159753258456qqW@localhost:5432/beer_recognition"

# Создаем асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True)

# Настраиваем асинхронные сессии
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Базовый класс для моделей
Base = declarative_base()

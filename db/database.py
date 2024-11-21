import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()
DATABASE_URL = os.getenv('DB_URL')

# Создаем асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True, isolation_level="AUTOCOMMIT")

# Настраиваем асинхронные сессии
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Базовый класс для моделей
Base = declarative_base()

from sqlalchemy.future import select
from db.database import AsyncSessionLocal  # асинхронная сессия
from db.models import User  # модель User для таблицы пользователей

# Функция проверки прав доступа пользователя
async def check_permissions(user_id: int, required_permission: int) -> bool:
    async with AsyncSessionLocal() as session:
        # Выполняем запрос на получение пользователя с данным user_id
        result = await session.execute(select(User).where(User.user_id == user_id))
        user_info = result.scalars().first()

        # Проверяем, существует ли пользователь и соответствует ли его permission
        if user_info is None or user_info.permissions < required_permission or user_info.permissions == 228:
            return False

    return True

# Функция для проверки, является ли пользователь "gromozeka"
async def is_gromozeka(user_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        # Выполняем запрос на получение пользователя с данным user_id
        result = await session.execute(select(User).where(User.user_id == user_id))
        user_info = result.scalars().first()

        # Проверяем, является ли пользователь "gromozeka" (permissions == 228)
        return user_info is not None and user_info.permissions == 228




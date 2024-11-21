from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.future import select
from db.database import AsyncSessionLocal
from db.models import Rating, Beer


async def load_votes(user_id):
    async with AsyncSessionLocal() as session:
        # Получаем все оценки для данного пользователя
        result = await session.execute(select(Rating).where(Rating.user_id == user_id))
        ratings = result.scalars().all()

        # Для каждой оценки пива сохраняем их идентификатор и оценку
        beer_ratings = {rating.beer_id: rating.rating for rating in ratings}

    return beer_ratings



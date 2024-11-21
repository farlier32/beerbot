from sqlalchemy.future import select
from db.database import AsyncSessionLocal  # асинхронная сессия
from db.models import Beer  # модель Beer для таблицы пива


# Асинхронная функция для загрузки списка пива из базы данных
async def load_beer_list():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Beer))
        beers = result.scalars().all()
        beer_list = [{'id': beer.beer_id, 'name': beer.name, 'brewery': beer.brewery} for beer in beers]
    return beer_list
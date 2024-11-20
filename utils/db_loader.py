# import pandas as pd

# def load_beer_list():
#    df = pd.read_csv(r'data/beer.csv')
#    beer_list = [{'id': i, 'name': name, 'brewery': brewery} for i, (name, brewery) in enumerate(zip(df['Пиво'], df['Пивоварня']), 1)]
#    return beer_list

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.database import AsyncSessionLocal  # асинхронная сессия
from db.models import Beer  # модель Beer для таблицы пива


# Асинхронная функция для загрузки списка пива из базы данных
async def load_beer_list():
    async with AsyncSessionLocal() as session:
        # Выполняем запрос на получение всех записей из таблицы Beer
        result = await session.execute(select(Beer))
        beers = result.scalars().all()

        # Преобразуем результат в список словарей
        beer_list = [{'id': beer.id, 'name': beer.name, 'brewery': beer.brewery} for beer in beers]

    return beer_list
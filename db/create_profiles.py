import asyncio
import logging
import pandas as pd
from sqlalchemy.future import select
from db.database import AsyncSessionLocal
from db.models import Beer

# Настройка логирования для SQLAlchemy
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

beer_list = []

profile_data = pd.read_csv(r'/beer info scrappers/untappd/profiles/Ahidnaja_Zaba_beers.csv')

async def beer_merge():
    async with AsyncSessionLocal() as session:
        for beer_name, rating in zip(profile_data['Пиво'], profile_data['Рейтинг']):
            result = await session.execute(select(Beer).where(Beer.name == beer_name))
            beer = result.scalars().first()
            if beer:
                beer_list.append((beer, rating))

def format_beer_data(beers):
    # Создаем DataFrame из списка объектов Beer
    data = {
        'name': [beer.name for beer, rating in beers],
        'brewery': [beer.brewery for beer, rating in beers],
        'style': [beer.style for beer, rating in beers],
        'release_date': [beer.release_date for beer, rating in beers],
        'rating': [beer.rating for beer, rating in beers],
        'ibu': [beer.ibu for beer, rating in beers],
        'hops': [beer.hops for beer, rating in beers],
        'malts': [beer.malts for beer, rating in beers],
        'additives': [beer.additives for beer, rating in beers],
        'alcohol': [beer.alcohol for beer, rating in beers],
        'og': [beer.og for beer, rating in beers],
        'personal_rating': [round(rating) for beer, rating in beers]
    }
    df = pd.DataFrame(data)
    return df

async def main():
    await beer_merge()
    # Форматируем данные пива в DataFrame
    df = format_beer_data(beer_list)
    # Сохраняем DataFrame в CSV файл
    df.to_csv('similar_beers.csv', index=False)
    print('Список схожих пив сохранен в similar_beers.csv')

# Запускаем main
if __name__ == "__main__":
    asyncio.run(main())
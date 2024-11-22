import os
import requests
from bs4 import BeautifulSoup as BS
from datetime import datetime
from sqlalchemy.future import select
from db.database import AsyncSessionLocal, Base
from sqlalchemy import Column, Integer, String, Float, Date, Text, TIMESTAMP

class Beer(Base):
    __tablename__ = "beers"
    beer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(1000), nullable=False)
    brewery = Column(String(1000))
    style = Column(String(255))
    alcohol = Column(Float)
    release_date = Column(Date)
    rating = Column(Float)
    ibu = Column(Integer)
    hops = Column(String(255))
    malts = Column(String(255))
    additives = Column(String(255))
    beer_links = Column(Text, unique=True)
    update_time = Column(TIMESTAMP)
    og = Column(Float)


async def parse_beer_info(input_path):
    count = 0

    def load_links(input_path):
        if os.path.exists(input_path):
            with open(input_path, 'r', encoding='utf-8') as file:
                return [link.strip() for link in file if link.strip()]
        return []

    async def load_existing_links(session):
        result = await session.execute(select(Beer.beer_links))
        return [row[0] for row in result.scalars().all()]

    def space_cleaner(data):
        for item in data:
            for key in item:
                item[key] = (' '.join(item[key].split())
                             .replace('" ', '"')
                             .replace(' "', '"')
                             .replace(', ', ',')
                             .replace(' ,', ',').strip())
        return data

    async def insert_data(session, data):
        for record in data:
            if not (await session.execute(select(Beer).filter_by(beer_links=record['Ссылка']))).scalar():
                beer = Beer(
                    name=record['Пиво'],
                    brewery=record.get(' Пивоварня', record.get('Пивоварни', '')),
                    style=record.get('Стиль', ''),
                    alcohol=float(record.get('Алкоголь', '0').replace('%', '').replace(',', '.')) if record.get('Алкоголь') and record['Алкоголь'] != 'N/A' else None,
                    release_date=datetime.strptime(record['Начало выпуска'], '%d.%m.%Y').date() if record.get('Начало выпуска') and record['Начало выпуска'] != 'N/A' else None,
                    rating=float(record.get('Рейтинг', '0').replace(',', '.')) if record.get('Рейтинг') and record['Рейтинг'] != 'N/A' else None,
                    ibu=int(record.get('Горечь', '0').split()[0]) if record.get('Горечь') and record['Горечь'] != 'N/A' else None,
                    hops=record.get('Хмель', ''),
                    malts=record.get('Солод', ''),
                    additives=record.get('Добавки', ''),
                    beer_links=record['Ссылка'],
                    update_time=datetime.now(),
                    og=float(record.get('Плотность', '0').replace(',', '.').replace('%', '')) if record.get(
                        'Плотность') and record['Плотность'] != 'N/A' else None
                )
                session.add(beer)
        await session.commit()

    beer_info_total = []

    links = load_links(input_path)

    async with AsyncSessionLocal() as session:
        existing_links = await load_existing_links(session)

        new_links = [link for link in links if link not in existing_links]

        for link in new_links:
            count += 1
            try:
                r = requests.get(link)
                html = BS(r.text, 'lxml')
                items = html.find_all('div', class_='tab-body')
                beer_name = html.find('div', class_='justify-content-md-start')
                title = beer_name.find('h1').text

                for el in items:
                    values = el.find_all(class_='value')
                    name = el.find_all(class_='name')
                    beer_info_temp = {}
                    for i in range(len(name)):
                        if name[i].text.rstrip(":") == "Пивоварни":
                            breweries = [a.text for a in values[i].find_all('a')]
                            beer_info_temp['Пивоварни'] = ', '.join(breweries)
                        else:
                            beer_info_temp[f'{name[i].text.rstrip(":")}'] = values[i].text.replace('\n', '')
                    beer_info_temp['Пиво'] = title
                    beer_info_temp['Ссылка'] = link  # Add the link to the dictionary
                    beer_info_total.append(beer_info_temp)
                print(f'Страниц с данными обработано - {count}', end='\r')
            except Exception as e:
                print(f'Ошибка: {e}')

            # Insert data into SQL database every 10 iterations
            if count % 10 == 0:
                beer_info_total = space_cleaner(beer_info_total)  # Clean spaces
                await insert_data(session, beer_info_total)
                beer_info_total = []  # Clear list after insertion

        # Final insert after all iterations
        if beer_info_total:
            beer_info_total = space_cleaner(beer_info_total)  # Clean spaces
            print(beer_info_total)
            await insert_data(session, beer_info_total)

    print('Парсинг окончен')
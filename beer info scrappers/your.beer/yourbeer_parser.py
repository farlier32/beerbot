# pylint: disable=import-error

from brewery_links_parser import parse_brewery_links
from beer_links_parser import parse_beer_links
from beer_info_parser import parse_beer_info
import asyncio

beer_links = r"C:\Users\Administrator\PycharmProjects\beerbot\beer info scrappers\your.beer\temp\beer_links.txt"
breweries_links = r"C:\Users\Administrator\PycharmProjects\beerbot\beer info scrappers\your.beer\temp\breweries_links.txt"


def data_base_update():

    # Вызов функции парсинга пивоварен
    try:
        print('Сбор ссылок на пивоварни:')
        parse_brewery_links()
    except Exception as e:
        print(f'\rОшибка в сборе ссылок на пивоварни: {e}', end='')
    
    # Вызов функции парсинга пива
    try:
        print('Сбор ссылок на пиво:')
        parse_beer_links(breweries_links, beer_links)
    except Exception as e:
        print(f'\rОшибка в сборе ссылок на пиво: {e}', end='')
    
    try:
        print('Сбор информации о пиве:')
        # Парсинг данных и вставка в базу данных
        asyncio.run(parse_beer_info(beer_links))

    except Exception as e:
        print(f'\rОшибка при сборе информации о пиве: {e}', end='')

if __name__ == "__main__":
    data_base_update()

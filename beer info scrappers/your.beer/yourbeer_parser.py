# pylint: disable=import-error

from brewery_links_parser import parse_brewery_links
from beer_links_parser import parse_beer_links
from beer_info_parser import parse_beer_info

beer_info = "beer info scrappers/your.beer/temp/beer_info.csv"
beer_links = "beer info scrappers/your.beer/temp/beer_links.txt"
breweries_links = "beer info scrappers/your.beer/temp/breweries_links.txt"


def data_base_update():

    # Вызов функции парсинга пивоварен
    try:
        print('Сбор ссылок на пивоварни:')
        parse_brewery_links()
    except Exception as e:
        print(f'Ошибка в сборе ссылок на пивоварни: {e}')
    
    # Вызов функции парсинга пива
    try:
        print('Сбор ссылок на пиво:')
        parse_beer_links(breweries_links, beer_links)
    except Exception as e:
        print(f'Ошибка в сборе ссылок на пиво: {e}')
    
    try:
        print('Сбор информации о пиве:')
        parse_beer_info(beer_links, beer_info)
    except Exception as e:
        print(f'Ошибка при сборе информации о пиве: {e}')

if __name__ == "__main__":
    data_base_update()

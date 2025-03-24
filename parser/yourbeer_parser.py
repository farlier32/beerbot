from .brewery_links import parse_brewery_links
from .beer_links import parse_beer_links
from .beer_info import parse_beer_info
import asyncio
import argparse


async def data_base_update(breweries_links, beer_links, parser_mode='', queue=None):

    if parser_mode in ['all', 'brewery']:

        try:
            print('Сбор ссылок на пивоварни:')
            parse_brewery_links(breweries_links)
        except Exception as e:
            print(f'\rОшибка в сборе ссылок на пивоварни: {e}', end='')


    elif parser_mode in ['all', 'beer']:
        try:
            print('Сбор ссылок на пиво:')
            parse_beer_links(breweries_links, beer_links)
        except Exception as e:
            print(f'\rОшибка в сборе ссылок на пиво: {e}', end='')
    elif parser_mode in ['all', 'info']:
        try:
            print('Сбор информации о пиве:')
            await parse_beer_info(beer_links)
        except Exception as e:
            print(f'\rОшибка в сборе информации о пиве: {e}', end='')
    if queue:
        await queue.put('complete')



def parse_args():
    parser = argparse.ArgumentParser(description='Run parsing script.')
    parser.add_argument('--mode', required=True, help='Parser mode (all, info, brewery, beer)')
    parser.add_argument('--breweries-links', required=True, help='Path to breweries links file')
    parser.add_argument('--beer-links', required=True, help='Path to beer links file')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    queue = asyncio.Queue()
    asyncio.run(data_base_update(args.breweries_links, args.beer_links, args.mode, queue))

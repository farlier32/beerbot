import pandas as pd
import os

from ujson import loads
import aiofiles

def load_beer_list():
    df = pd.read_csv(r'data/beer.csv')
    beer_list = [{'id': i, 'name': name, 'brewery': brewery} for i, (name, brewery) in enumerate(zip(df['Пиво'], df['Пивоварня']), 1)]
    return beer_list

# async def get_json(filename: str) -> list:
#     path = f"data/{filename}"
#     if os.path.exists(path):
#         async with aiofiles.open(path)

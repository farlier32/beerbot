# pylint: disable=import-error

import requests
from bs4 import BeautifulSoup as BS
import os
import pandas as pd

def parse_beer_info(input_path, output_path):
    count = 0

    def load_links(input_path):
        if os.path.exists(input_path):
            with open(input_path, 'r', encoding='utf-8') as file:
                return [link.strip() for link in file if link.strip()]
        return []

    def load_existing_links(output_path):
        if os.path.exists(output_path):
            df = pd.read_csv(output_path)
            return df['Ссылка'].tolist()
        return []

    beer_info_total = []

    links = load_links(input_path)
    existing_links = load_existing_links(output_path)

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

        # Save the file every 10 iterations
        if count % 10 == 0:
            df = pd.DataFrame(beer_info_total)

            # Переименование колонки " Пивоварня" в "Пивоварня"
            df.rename(columns={' Пивоварня': 'Пивоварня'}, inplace=True)

            # Изменение столбца "Пивоварни" на "Пивоварня", если строка не пустая
            if 'Пивоварни' in df.columns:
                df['Пивоварня'] = df['Пивоварня'].combine_first(df['Пивоварни'])
                df.drop(columns=['Пивоварни'], inplace=True)

            # Перестановка столбцов, чтобы "Ссылка" была последней
            columns = [col for col in df.columns if col != 'Ссылка'] + ['Ссылка']
            df = df[columns]

            df.to_csv(output_path, index=False)

    # Final save after all iterations
    df = pd.DataFrame(beer_info_total)

    # Переименование колонки " Пивоварня" в "Пивоварня"
    df.rename(columns={' Пивоварня': 'Пивоварня'}, inplace=True)

    # Изменение столбца "Пивоварни" на "Пивоварня", если строка не пустая
    if 'Пивоварни' in df.columns:
        df['Пивоварня'] = df['Пивоварня'].combine_first(df['Пивоварни'])
        df.drop(columns=['Пивоварни'], inplace=True)

    # Перестановка столбцов, чтобы "Ссылка" была последней
    columns = [col for col in df.columns if col != 'Ссылка'] + ['Ссылка']
    df = df[columns]

    df.to_csv(output_path, index=False)
    print('Парсинг окончен')

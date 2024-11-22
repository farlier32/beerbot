# pylint: disable=import-error

import requests
from bs4 import BeautifulSoup
import os
import sys

def load_links(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return [link.strip() for link in file if link.strip()]
    return []

def save_links(file_path, links):
    with open(file_path, 'a', encoding='utf-8') as file:
        for link in links:
            file.write(link + '\n')

def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def parse_beer_links(breweries_links_path, beer_links_path):
    links = load_links(breweries_links_path)
    existing_links = set(load_links(beer_links_path))
    
    for burl in links:
        page_number = 1
        
        while True:
            paginated_url = f"{burl}?sort=date&order=desc&page={page_number}"
            html_code = fetch_page(paginated_url)
            soup = BeautifulSoup(html_code, 'html.parser')
            
            # Найти все ссылки с классом d-flex b-card-wrapper
            new_links = set()
            for card in soup.find_all('div', class_='d-flex b-card-wrapper'):
                link = card.find('a', href=True)
                if link:
                    new_links.add(link['href'])
            
            # Если новых ссылок нет, прекращаем пагинацию
            if not new_links:
                break
            
            # Добавляем новые ссылки к существующим
            new_links = new_links - existing_links
            if new_links:
                save_links(beer_links_path, new_links)
                existing_links.update(new_links)
            
            print(f"\rЗагружена страница {page_number} для {burl}", end='')
            page_number += 1

    print()  # Печатает новую строку после завершения

import requests
from bs4 import BeautifulSoup
import os
from colorama import Fore, Style, init
from urllib.parse import unquote, quote
import re

init()

def load_links(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return [unquote(link.strip()) for link in file if link.strip()]
    return []

def save_links(file_path, links):
    with open(file_path, 'w', encoding='utf-8') as file:
        for link in links:
            file.write(link + '\n')

def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def parse_beer_links(breweries_links_path, beer_links_path, max_pages=999):
    links = load_links(breweries_links_path)
    existing_links = set(load_links(beer_links_path))
    all_new_links = set()
    special_char_pattern = re.compile(r'%[0-9A-Fa-f]{2}')

    for burl in links:
        if special_char_pattern.search(burl):
            max_pages = 5  # Ограничиваем до одной страницы для ссылок с особыми символами

        page_number = 1
        last_new_links = set()
        while page_number <= max_pages:
            try:
                paginated_url = f"{burl}?sort=date&order=desc&page={page_number}"
                html_code = fetch_page(paginated_url)
                soup = BeautifulSoup(html_code, 'html.parser')

                new_links = set()
                for card in soup.find_all('div', class_='d-flex b-card-wrapper'):
                    link = card.find('a', href=True)
                    if link:
                        new_links.add(link['href'])

                if not new_links or new_links == last_new_links:
                    break

                all_new_links.update(new_links)
                last_new_links = new_links
                print(Style.RESET_ALL + '\r', end='')
                print(Fore.RED + f"\rЗагружена страница {page_number} для {burl}", end='')
                print(Style.RESET_ALL + '\r', end='')
                page_number += 1
            except requests.HTTPError as e:
                print(Fore.RED + f"\nОшибка в сборе ссылок на пиво: {e}")
                links.remove(burl)
                break

        if special_char_pattern.search(burl):
            max_pages = 999 # Сбрасываем max_pages на исходное значение для остальных ссылок

    print()

    missing_links = existing_links - all_new_links
    if missing_links:
        print(f"Удалено устаревших ссылок: {len(missing_links)}")

    save_links(beer_links_path, all_new_links)

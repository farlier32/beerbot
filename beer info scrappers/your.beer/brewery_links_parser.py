# pylint: disable=import-error

import requests
from bs4 import BeautifulSoup
import os
import time

def load_links(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return [link.strip() for link in file if link.strip()]
    return []

def save_links(file_path, links):
    existing_links = set(load_links(file_path))
    new_links = [link for link in links if link not in existing_links]
    
    if new_links:
        with open(file_path, 'a', encoding='utf-8') as file:
            for link in new_links:
                file.write(link + '\n')

def get_page_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def parse_brewery_links():
    base_url = 'https://your.beer/breweries'
    file_path = r"C:\Users\Administrator\PycharmProjects\beerbot\beer info scrappers\your.beer\temp\breweries_links.txt"
    page_counter = 1

    while True:
        url = f"{base_url}/?page={page_counter}\r"
        print(f"\rСбор по ссылке: {page_counter}: {url}", end='')
        html_content = get_page_content(url)
        soup = BeautifulSoup(html_content, 'html.parser')

        # Проверка на наличие контента
        cards = soup.find_all('div', class_='d-flex b-card-wrapper')
        if not cards:
            print("Контент закончился, прекращаем пагинацию.")
            break

        links = []
        for card in cards:
            link_tag = card.find('a', href=True)
            if link_tag:
                links.append(link_tag['href'])

        save_links(file_path, links)
        print(f"Сохранено {len(links)} ссылок с страницы {page_counter}.\r")

        page_counter += 1
        time.sleep(1)  # Небольшая пауза между запросами

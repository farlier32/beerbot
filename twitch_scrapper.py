from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import webbrowser

import time

start_time = time.time()

# ВРЕМЯ РАБОТЫ СКРИПТА В СЕКУНДАХ
timeout = 15000

options = Options()
# options.add_argument("--headless=new")
options.add_argument("--mute-audio")
options.add_argument("--window-size=1920,1080")
options.add_argument("start-maximized")
options.add_argument('--enable-chrome-browser-cloud-management')

#ССЫЛКА НА СТРИМ ТВИЧ
url = 'https://www.twitch.tv/dawgonosik'

# Укажите свой браузер(всего в селениуме Chrome, Edge, Firefox, Opera
driver = webdriver.Edge(options=options)
driver.get(url=url)

opened_links = set()

while True:
    try:
        text_scrappy = driver.find_elements(By.TAG_NAME, value="a")

        links = set()
        for element in text_scrappy:
            link = element.get_attribute('href')
            # !!!! вставить не полную ссылку для сбора и открытия пример: boosty.to/xxxxx/gift/ !!!!
            if 'boosty.to/dawgonosik/subscription-level/' in link or 'boosty.to/dawgonosik/gift/' in link:
                links.add(link)
        links_list = list(links)
        for i in links_list:
            if i not in opened_links:

                # ССЫЛКИ БУДУТ ОТКРЫВАТЬСЯ В ДЕФОЛТНОМ БРАУЗЕРЕ, ЗАЛОГИНЬТЕСЬ НА САЙТЕ, ДЛЯ КОТОРОГО СОБИРАЕТЕ ГИФТЫ
                webbrowser.open(i)
                opened_links.add(i)
        
        pass
    except Exception as e:
        # Часто из-за того что ссылок не будет - в консоль будет выдавать повторный запуск, не страшно
        print("Повторный запуск кода...")
        if time.time() - start_time > timeout:
            print("Время вышло, прерывание цикла...")
            driver.close()
            driver.quit()
            break
        continue
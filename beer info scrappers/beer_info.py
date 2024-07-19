from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time
import pickle


options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166")

driver = webdriver.Chrome(options=options)

count = 0
try:
    driver.get(url='https://untappd.com/')
    for cookie in pickle.load(open('beer info scrappers/untappd_cookies', 'rb')):
        driver.add_cookie(cookie)
    driver.get(url='https://untappd.com/search?q=a&type=beer&sort=')
    try:
        while True:
            # Прокрутка вниз
            driver.execute_script("window.scrollBy(0, 5000);")
            time.sleep(5)
            show_more_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='button yellow more_search track-click']"))
            )
            # Нажатие на ссылку
            show_more_link.click()
            # Пауза, пока загрузится страница
            count += 1
            print(f"    Появился новый контент, прокручиваем дальше (Всего свайпов: {count})", end='\r')
    except:
        print("Прокрутка завершена")
    time.sleep(5)

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    # Поиск всех элементов пива на странице
    beers = soup.find_all('div', class_='beer-item')

    # Сбор данных для каждого пива
    with open('beer info scrappers/beers.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Запись заголовков столбцов
        writer.writerow(["Пиво", "Пивоварня", "Стиль", "ABV", "IBU", "Рейтинг"])
        for beer in beers:
            name_element = beer.find('p', class_='name')
            name = name_element.text.strip() if name_element else None

            brewery_element = beer.find('p', class_='brewery')
            brewery = brewery_element.text.strip() if brewery_element else None

            style_element = beer.find('p', class_='style')
            style = style_element.text.strip() if style_element else None

            abv_element = beer.find('p', class_='abv')
            abv = abv_element.text.strip() if abv_element else None

            ibu_element = beer.find('p', class_='ibu')
            ibu = ibu_element.text.strip() if ibu_element else None

            rating_element = beer.find('div', class_='caps')
            rating = rating_element.get('data-rating') if rating_element else None

        # Запись данных пива в файл CSV
            writer.writerow([name, brewery, style, abv, ibu, rating])

except Exception as ex:
        print(ex)

finally:
    driver.close()
    driver.quit()
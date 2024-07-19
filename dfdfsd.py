# Парсинг отзывов с 'https://yu-klinik.relax.by/otzyvy/', 'https://yu-klinik.103.by/otzyvy/'

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd


# procedure_list = [
#     'Стоматологи-ортопеды', 'Ортопедическая стоматология', 'Протезирование зубов', 'Изготовление зубных протезов', 'Хирургическая стоматология', 'Лечение кариеса', 'Ортодонтия',
#     'Коронки из диоксида циркония', 'Удаление зубов', 'Терапевтическая стоматология', 'Брекеты', 'Чистка зубов Air Flow', 'Имплантация зубов', 'Лечение зубов и профилактика',
#     'Лечение пульпита', 'Удаление ретинированного зуба', 'Пломбирование зубов', 'Рентген-диагностика зубов', 'Консультация врача', 'Стоматологи-хирурги', 'Отбеливание зубов',
#     'Бюгельное протезирование зубов', 'Изготовление зубных коронок', 'Коронка металлокерамическая', 'Гигиена полости рта', 'Анализы и диагностика', 'Лечение зубов лазером',
#     'Реставрационные виниры', 'Телерентгенография в стоматологии', 'Реставрация зубов', 'Снятие брекетов', 'Исправление прикуса', 'Накладки на зубы', 'Детская стоматология',
#     'Виниры', 'Ультразвуковая чистка зубов', 'Выравнивание зубов', 'Консультация врача-ортодонта'
#                            ]
links = ['https://yu-klinik.relax.by/otzyvy/', 'https://yu-klinik.103.by/otzyvy/']

for link in links:
    driver = webdriver.Edge()

    review = []
    count = 0
    try:
        driver.get(url=link)
        try:
            while True:
                # Прокрутка вниз
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                news_link = driver.find_element(By.CLASS_NAME, value='ContentBox__footer').click()
                # Пауза, пока загрузится страница
                time.sleep(2)
                count += 1
                print(f"    Появился новый контент, прокручиваем дальше (Всего свайпов: {count})", end='\r')
        except:
            print("Прокрутка завершена")

    except Exception as ex:
        print(ex)
    time.sleep(5)

    #Сбор комментариев


    review_comments = []
    reviewer = []
    review_rating = []
    review_date = []
    # therapist = []
    # procedure = []


            

    review_comments_all = driver.find_elements(By.CLASS_NAME, value='Review__TextInner')
        
        


    reviewer_all = driver.find_elements(By.CLASS_NAME, value='Review__AuthorName')


    yu_klinik = ['Ю-КЛИНИК', 'Администрация', '"Ю-КЛИНИК"', 'администрация', 'Администрация "Ю-КЛИНИК"', 'Ю-КЛИНИК!']
    for i in range(len(reviewer_all)):
        if reviewer_all[i].get_attribute('textContent') not in yu_klinik:
            review_comments.append(review_comments_all[i].get_attribute('textContent').replace("...", ""))
            reviewer.append(reviewer_all[i].get_attribute('textContent'))
            


    # Сбор оценок
            

    review_rating_str = driver.find_elements(By.XPATH, value="//div[@class='Rating Rating--yellow Rating--small']")
    for i in review_rating_str:
        if i.get_attribute('title') == 'Отлично':
            review_rating.append(5)
        elif i.get_attribute('title') == 'Очень хорошо':
            review_rating.append(4)
        elif i.get_attribute('title') == 'Неплохо':
            review_rating.append(3)
        elif i.get_attribute('title') == 'Плохо':
            review_rating.append(2)
        elif i.get_attribute('title') == 'Ужасно':
            review_rating.append(1)



    # Сбор даты написания комментария
            

    datetime = driver.find_elements(By.XPATH, value="//time[@class='Review__DateTime MenuItem--mini u-uppercase']")
    # Так как тегов time по 2 на комментарий - выбираю только нечётные, чтобы отсеять ненужные дубликаты.
    for i in datetime:
        review_date.append(i.get_attribute('textContent'))
        


    # Сбор лечащих врачей и процедур
        
        # нужно будет написать фильтр, разбивающий врачей и процедуры на 2 столбца, а так же автоматически заполняющий пропуски

    # therapist_procedure = driver.find_elements(By.XPATH, value="//span[@class='Review__footerLinkText u-ellipsis']")
    # temp = []
    # for i in therapist_procedure:
    #     temp.append(f"{i.get_attribute('textContent')}\n")

    print(len(datetime))
    print(len(review_comments))
    print(len(reviewer))
    print(len(review_rating))



    df = pd.DataFrame({'Имя': reviewer[0:660],'Комментарий': review_comments[0:660],  'Дата': review_date[0:660], 'Оценка': review_rating[0:660]})

    df.to_csv(f"Yu-Clinic/reviews/reviews_{link.replace('https://yu-klinik.', '').replace('/otzyvy/', '')}.csv")
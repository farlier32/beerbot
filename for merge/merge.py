import pandas as pd

# Загрузка первого CSV файла
df1 = pd.read_csv('for merge/beer_info.csv')

# Загрузка второго CSV файла
df2 = pd.read_csv('for merge/beer_info_new.csv')

# Объединение файлов по общим столбцам
common_columns = ['Пиво', 'Пивоварня', 'Стиль', 'Алкоголь', 'Начало выпуска', 'Рейтинг', 'Горечь', 'Плотность', 'Ссылка']
df_combined = pd.concat([df1, df2[common_columns]], ignore_index=True)

# Сохранение объединенного файла
df_combined.to_csv('for merge/beer.csv', index=True)

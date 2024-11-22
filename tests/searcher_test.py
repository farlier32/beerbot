


def load_beer_list():
    # Пример списка пива
    return [
        {'brewery': 'Лидское Kriek', 'beer': 'Magnum IPA'},
        {'brewery': 'Лидское Пшеничное', 'beer': 'Lubelski Lager'},
        {'brewery': 'Kriek Absolute', 'beer': 'Grogs Stout'},
        {'brewery': 'Gromozeka', 'beer': 'Grogs Stout'},
        {'brewery': 'Sozhski #2', 'beer': 'Grogs Stout'},
        {'brewery': 'DDT', 'beer': 'Grogs Stout'}
    ]

def search_by_breweries(query):
    beer_list = load_beer_list()  # Загружаем список пива
    query_lower = query.lower()  # Преобразуем запрос в нижний регистр для нечувствительности к регистру
    search_results = [
        brewery for brewery in beer_list if query_lower in brewery['brewery'].lower()
    ]  # Ищем полное совпадение подстроки в названии пивоварни
    return search_results

def main():
    query = "Лидское K"
    results = search_by_breweries(query)
    print("Результаты поиска:", results)

if __name__ == "__main__":
    main()



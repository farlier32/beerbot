from utils.db_loader import load_beer_list
async def search_by_beer(query):
    beer_list = await load_beer_list()  # Загрузите список пива
    query = query.lower()
    search_results = [beer for beer in beer_list if beer['name'].lower().startswith(query)]  # Ищите совпадения
    return search_results

async def search_by_breweries(query):
    beer_list = await load_beer_list()  # Используем await для загрузки списка пива
    query_words = query.lower().split()  # Разбейте запрос на отдельные слова
    search_results = [
        brewery for brewery in beer_list if any(word in brewery['brewery'].lower() for word in query_words)
    ]  # Ищите совпадения
    return search_results
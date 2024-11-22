from utils.db_loader import load_beer_list
async def search_by_beer(query):
    beer_list = await load_beer_list()  # Загрузите список пива
    query_lower = query.lower()
    search_results = [
        beer for beer in beer_list if query_lower in beer['name'].lower()
    ]  # Ищите совпадения
    return search_results

async def search_by_breweries(query):
    beer_list = await load_beer_list()  # Загружаем список пива
    query_lower = query.lower()  # Преобразуем запрос в нижний регистр для нечувствительности к регистру
    search_results = [
        brewery for brewery in beer_list if query_lower in brewery['brewery'].lower()
    ]  # Ищем полное совпадение подстроки в названии пивоварни
    return search_results
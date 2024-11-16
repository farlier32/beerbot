from aiogram import types, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.state import State, StatesGroup
from aiogram.types.callback_query import CallbackQuery
from utils.searcher import search_by_beer, search_by_breweries
import json
from utils.votes import update_vote_results
from utils.db_loader import load_beer_list
import keyboards.reply as kb
import utils.messages as text
from aiogram import Router
from utils.permissions import is_gromozeka
from utils.messages import gromozeka



router = Router()

current_page = 1
items_per_page = 10

search_results = []


@router.message(Command("start"))
async def start_handler(msg: Message):


    user_id = msg.from_user.id
    first_name = msg.from_user.first_name
    last_name = msg.from_user.last_name
    username = msg.from_user.username
    if is_gromozeka(user_id):
        await msg.answer(gromozeka)
        return


    new_user = {'id': user_id, 
                'nick': username, 
                'name': first_name, 
                'last_name': last_name, 
                'permissions': 0}
    with open('data/users.json', encoding='utf8') as f:
        user_data = json.load(f)

        # Проверяем, является ли пользователь новым
        existing_users = [user for user in user_data['users'] if user['id'] == user_id]

        if not existing_users:
            # Если пользователь новый, добавляем его в базу данных
            user_data['users'].append(new_user)

        else:
            # Если пользователь уже существует, обновляем его данные
            existing_user = existing_users[0]
            existing_user['nick'] = username
            existing_user['name'] = first_name
            existing_user['last_name'] = last_name

        with open('data/users.json', 'w', encoding='utf8') as outfile:
            json.dump(user_data, outfile, ensure_ascii=False, indent=2)
    
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)





@router.message(F.text == "Меню")
async def menu(msg: Message):
    user_id = msg.from_user.id

    if is_gromozeka(user_id):
        await msg.answer(gromozeka)
        return
    await msg.answer(text.menu, reply_markup=kb.menu)

@router.message(F.text == "Мой профиль 📂")
async def profile_handler(message: types.Message):
    user_id = message.from_user.id

    if is_gromozeka(user_id):
        await message.answer(gromozeka)
        return
    await message.answer("Выберите действие:", reply_markup=kb.user_menu)
    
@router.message(F.text == "Инфо🧾")
async def info_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.first_name
    if is_gromozeka(user_id):
        await message.answer(gromozeka)
        return

    # Загрузите данные о голосах из файла или базы данных
    with open('data/votes.json', 'r', encoding='utf8') as f:
        vote_data = json.load(f)
        user_votes = vote_data.get(str(user_id), {})

    # Подсчитайте количество оценок пользователя
    num_votes = len(user_votes)

    await message.answer(f"Имя:  {username}\nКоличество оценок: {num_votes}⭐️")

@router.message(F.text == "Список мест 🏘")
async def places_handler(message: types.Message):
    user_id = message.from_user.id

    if is_gromozeka(user_id):
        await message.answer(gromozeka)
        return

    try:
        # Загрузка данных о местах из places.json
        with open('data/places.json', 'r', encoding='utf8') as f:
            places_data = json.load(f)

        # Создание кнопок для каждого места
        buttons = [[InlineKeyboardButton(text=place, callback_data=f"place_{place}")] for place in places_data.keys()]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer("Список мест:", reply_markup=markup)

    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

@router.callback_query(F.data.startswith("place_"))
async def place_callback_handler(cq: CallbackQuery):
    try:
        # Извлеките название места из данных обратного вызова
        place_name = cq.data.split("_")[1]

        # Загрузка списка пива
        beer_list = load_beer_list()

        # Загрузка данных о местах из places.json
        with open('data/places.json', 'r', encoding='utf8') as f:
            places_data = json.load(f)

        # Получение списка пива для выбранного места
        beers_in_place = [beer for beer in beer_list if beer['id'] in places_data[place_name]['beers']]
        beer_ids = [beer['id'] for beer in beers_in_place]

        # Создание кнопок для каждого пива
        buttons = [[InlineKeyboardButton(text=beer['name'], callback_data=f"beer_{beer['id']}")] for beer in beers_in_place]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        await cq.message.answer(f"Место: {place_name}\nПиво:", reply_markup=markup)

    except Exception as e:
        await cq.message.answer(f"Произошла ошибка: {e}")

@router.callback_query(F.data.startswith("beer_"))
async def beer_callback_handler(cq: CallbackQuery):
    try:
        # Извлеките идентификатор пива из данных обратного вызова
        beer_id = int(cq.data.split("_")[1])

        # Найдите пиво в списке пива
        beer_list = load_beer_list()
        selected_beer = next((beer for beer in beer_list if beer['id'] == beer_id), None)
        
        if selected_beer is None:
            await cq.message.answer("Произошла ошибка: пиво не найдено.")
            return

        # Создайте клавиатуру с кнопками "Нравится" и "Не нравится"
        buttons = [
            [InlineKeyboardButton(text="👍", callback_data=f"like_{beer_id}"),
            InlineKeyboardButton(text="👎", callback_data=f"dislike_{beer_id}")]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        # Отправьте сообщение с названием выбранного пива и клавиатурой
        await cq.message.answer(f"Вы выбрали: {selected_beer['name']}", reply_markup=markup)

    except Exception as e:
        await cq.message.answer(f"Произошла ошибка: {e}")


@router.callback_query(F.data.startswith("like_beer_"))
async def like_callback_handler_place(cq: CallbackQuery):
    try:
        # Извлеките идентификатор пива из данных обратного вызова
        beer_id = int(cq.data.split("like_beer_")[1])
        user_id = cq.from_user.id

        # Обновите результаты голосования
        update_vote_results(user_id, beer_id, "like")

        await cq.answer("Ваш голос учтен!")
        await cq.message.delete()

    except Exception as e:
        await cq.answer(f"Произошла ошибка: {e}")

@router.callback_query(F.data.startswith("dislike_beer_"))
async def dislike_callback_handler_place(cq: CallbackQuery):
    try:
        # Извлеките идентификатор пива из данных обратного вызова
        beer_id = int(cq.data.split("dislike_beer_")[1])
        user_id = cq.from_user.id

        # Обновите результаты голосования
        update_vote_results(user_id, beer_id, "dislike")

        await cq.answer("Ваш голос учтен!")
        await cq.message.delete()

    except Exception as e:
        await cq.answer(f"Произошла ошибка: {e}")







@router.message(F.text == "Мои оценки⭐️")
async def user_rating_handler(message: types.Message):
    user_id = message.from_user.id

    if is_gromozeka(user_id):
        await message.answer(gromozeka)
        return
    try:
        global current_page
        user_id = message.from_user.id
        with open('data/votes.json', 'r', encoding='utf8') as f:
            vote_data = json.load(f)
            user_votes = vote_data.get(str(user_id), {})
            liked_beers_ids = [int(beer_id) for beer_id, vote in user_votes.items() if vote == "like"]
            disliked_beers_ids = [int(beer_id) for beer_id, vote in user_votes.items() if vote == "dislike"]

        beer_list = load_beer_list()
        liked_beers = [beer for beer in beer_list if beer['id'] in liked_beers_ids]
        disliked_beers = [beer for beer in beer_list if beer['id'] in disliked_beers_ids]

        if not liked_beers and not disliked_beers:
            await message.answer("Вы еще не лайкнули или дизлайкнули ни одного пива.")
            return

        # Объедините списки понравившихся и не понравившихся пив
        all_beers = liked_beers + disliked_beers

        # Определите, какие элементы отображать на основе текущей страницы
        start = (current_page - 1) * 10
        end = start + 10
        page_items = all_beers[start:end]

        buttons = [[InlineKeyboardButton(text=f"{'👍' if beer in liked_beers else '👎'} {beer['name']} / {beer['brewery']}", callback_data=f"item_{beer['id']}")] for beer in page_items]
        navigation_buttons = []
        if current_page > 1:
            navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page:{current_page - 1}"))
        if end < len(all_beers):
            navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"page:{current_page + 1}"))
        if navigation_buttons:
            buttons.append(navigation_buttons)
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer("Ваши оценки:", reply_markup=markup)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")



class SearchState(StatesGroup):
    WaitingForBeerQuery = State()
    WaitingForBreweryQuery = State()





@router.message(F.text == "Поиск 🔍")
async def search_handler(message: types.Message):
    user_id = message.from_user.id

    if is_gromozeka(user_id):
        await message.answer(gromozeka)
        return
    await message.answer("Выберите тип поиска:", reply_markup=kb.search_menu)

@router.message(F.text == "Поиск по пивоварням")
async def search_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if is_gromozeka(user_id):
        await message.answer(gromozeka)
        return
    try:
        # Запросите у пользователя ввод для поиска пива
        await message.answer("Введите название пивоварни, которую вы ищете:")
        await state.set_state(SearchState.WaitingForBreweryQuery.state)  # Используйте .state
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

@router.message(F.text == "Поиск по пиву")
async def search_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if is_gromozeka(user_id):
        await message.answer(gromozeka)
        return
    try:
        # Запросите у пользователя ввод для поиска пива
        await message.answer("Введите название пива, которое вы ищете:")
        await state.set_state(SearchState.WaitingForBeerQuery.state)  # Используйте .state
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

@router.message(F.text.lower() == "вернуться в меню")
async def search_handler(message: types.Message, state: FSMContext):
    await message.answer("Возвращаемся в меню...", reply_markup=kb.menu)
    await state.clear()



@router.message(SearchState.WaitingForBeerQuery)
async def get_search_results_beer(message: Message, state: FSMContext):
    try:
        global search_results
        # Используйте введенный пользователем текст для поиска пива
        search_query = message.text
        search_results = search_by_beer(search_query)
        if not search_results:
            await message.answer("К сожалению, по вашему запросу ничего не найдено.")
            return

        # Генерация кнопок с результатами поиска
        page = 1  # Начальная страница
        start = (page - 1) * 10
        end = start + 10
        page_items = search_results[start:end]
        buttons = [[InlineKeyboardButton(text=f"{item['name']} / ({item['brewery']})", callback_data=f"item_{item['id']}")] for item in page_items]
        navigation_buttons = []
        if end < len(search_results):
            navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"search_results:{page + 1}"))
        if navigation_buttons:
            buttons.append(navigation_buttons)
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer("Результаты поиска:", reply_markup=markup)

    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")


@router.message(SearchState.WaitingForBreweryQuery)
async def get_search_results_breweries(message: Message, state: FSMContext):
    try:
        global search_results
        # Используйте введенный пользователем текст для поиска пива
        search_query = message.text
        search_results = search_by_breweries(search_query)
        if not search_results:
            await message.answer("К сожалению, по вашему запросу ничего не найдено.")
            return

        # Генерация кнопок с результатами поиска
        page = 1  # Начальная страница
        start = (page - 1) * 10
        end = start + 10
        page_items = search_results[start:end]
        buttons = [[InlineKeyboardButton(text=f"{item['name']} / ({item['brewery']})", callback_data=f"item_{item['id']}")] for item in page_items]
        navigation_buttons = []
        if end < len(search_results):
            navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"search_results:{page + 1}"))
        if navigation_buttons:
            buttons.append(navigation_buttons)
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer("Результаты поиска:", reply_markup=markup)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

@router.callback_query(F.data.startswith("item_"))
async def item_callback_handler(cq: CallbackQuery):
    try:
        # Извлеките идентификатор пива из данных обратного вызова
        beer_id = int(cq.data.split("_")[1])
        
        # Найдите пиво в списке пива
        beer_list = load_beer_list()
        selected_beer = next((beer for beer in beer_list if beer['id'] == beer_id), None)
        
        if selected_beer is None:
            await cq.message.answer("Произошла ошибка: пиво не найдено.")
            return

        # Создайте клавиатуру с кнопками "Нравится" и "Не нравится"
        buttons = [
            [InlineKeyboardButton(text="👍", callback_data=f"like_{beer_id}"),
            InlineKeyboardButton(text="👎", callback_data=f"dislike_{beer_id}")]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        # Отправьте сообщение с названием выбранного пива и клавиатурой
        await cq.message.answer(f"Вы выбрали: {selected_beer['name']}", reply_markup=markup)

    except Exception as e:
        await cq.message.answer(f"Произошла ошибка: {e}")

@router.callback_query(F.data.startswith("page:"))
async def page_callback_handler(cq: CallbackQuery):
    try:
        global current_page
        # Извлеките номер страницы из данных обратного вызова
        current_page = int(cq.data.split(":")[1])

        user_id = cq.from_user.id
        with open('data/votes.json', 'r', encoding='utf8') as f:
            vote_data = json.load(f)
            user_votes = vote_data.get(str(user_id), {})
            liked_beers_ids = [int(beer_id) for beer_id, vote in user_votes.items() if vote == "like"]
            disliked_beers_ids = [int(beer_id) for beer_id, vote in user_votes.items() if vote == "dislike"]

        beer_list = load_beer_list()
        liked_beers = [beer for beer in beer_list if beer['id'] in liked_beers_ids]
        disliked_beers = [beer for beer in beer_list if beer['id'] in disliked_beers_ids]

        # Объедините списки понравившихся и не понравившихся пив
        all_beers = liked_beers + disliked_beers

        # Определите, какие элементы отображать на основе текущей страницы
        start = (current_page - 1) * 10
        end = start + 10
        page_items = all_beers[start:end]

        buttons = [[InlineKeyboardButton(text=f"{'👍' if beer in liked_beers else '👎'} {beer['name']} / {beer['brewery']}", callback_data=f"item_{beer['id']}")] for beer in page_items]
        navigation_buttons = []
        if current_page > 1:
            navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page:{current_page - 1}"))
        if end < len(all_beers):
            navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"page:{current_page + 1}"))
        if navigation_buttons:
            buttons.append(navigation_buttons)
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        await cq.message.edit_text("Ваши оценки:", reply_markup=markup)
    except Exception as e:
        await cq.answer(f"Произошла ошибка: {e}")



@router.callback_query(F.data.startswith("search_results:"))
async def search_results_callback_handler(cq: CallbackQuery, state: FSMContext):
    try:
        global current_page
        current_page = int(cq.data.split(":")[1])
        start = (current_page - 1) * 10
        end = start + 10
        page_items = search_results[start:end]
        
        # Генерация кнопок внутри обработчика
        buttons = [[InlineKeyboardButton(text=f"{item['name']} / ({item['brewery']})", callback_data=f"item_{item['id']}")] for item in page_items]
        navigation_buttons = []
        if start > 0:
            navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"search_results:{current_page - 1}"))
        if end < len(search_results):
            navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"search_results:{current_page + 1}"))
        if navigation_buttons:
            buttons.append(navigation_buttons)
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        await cq.message.edit_text("Результаты поиска:", reply_markup=markup)
    except Exception as e:
        await cq.message.answer(f"Произошла ошибка: {e}")






@router.callback_query(F.data.startswith("like_"))
async def like_callback_handler(cq: CallbackQuery):
    try:
        # Извлеките идентификатор пива из данных обратного вызова
        beer_id = int(cq.data.split("_")[1])
        user_id = cq.from_user.id

        # Найдите пиво в списке пива
        beer_list = load_beer_list()
        selected_beer = next((beer for beer in beer_list if beer['id'] == beer_id), None)
        
        if selected_beer is None:
            await cq.message.answer("Произошла ошибка: пиво не найдено.")
            return

        # Обновите результаты голосования
        update_vote_results(user_id, selected_beer['id'], "like")

        await cq.answer("Ваш голос учтен!")
        await cq.message.delete()

    except Exception as e:
        await cq.answer(f"Произошла ошибка: {e}")

@router.callback_query(F.data.startswith("dislike_"))
async def dislike_callback_handler(cq: CallbackQuery):
    try:
        # Извлеките идентификатор пива из данных обратного вызова
        beer_id = int(cq.data.split("_")[1])
        user_id = cq.from_user.id

        # Найдите пиво в списке пива
        beer_list = load_beer_list()
        selected_beer = next((beer for beer in beer_list if beer['id'] == beer_id), None)
        
        if selected_beer is None:
            await cq.message.answer("Произошла ошибка: пиво не найдено.")
            return

        # Обновите результаты голосования
        update_vote_results(user_id, selected_beer['id'], "dislike")

        await cq.answer("Ваш голос учтен!")
        await cq.message.delete()

    except Exception as e:
        await cq.answer(f"Произошла ошибка: {e}")


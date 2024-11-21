from aiogram import types, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.state import State, StatesGroup
from aiogram.types.callback_query import CallbackQuery
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest



import keyboards.reply as kb
import utils.messages as text
from utils.searcher import search_by_beer, search_by_breweries
from utils.db_loader import load_beer_list
from utils.permissions import is_gromozeka
from utils.messages import gromozeka
from sqlalchemy import func
from sqlalchemy.future import select
from db.database import AsyncSessionLocal
from db.models import *



router = Router()

search_page = 1
rating_page = 1
items_per_page = 10

search_results = []


@router.message(Command("start"))
async def start_handler(msg: Message):
    user_id = msg.from_user.id
    first_name = msg.from_user.first_name
    last_name = msg.from_user.last_name
    nickname = msg.from_user.username

    if await is_gromozeka(user_id):
        await msg.answer(gromozeka)
        return

    # Создание нового пользователя
    new_user = User(
        user_id=user_id,
        nickname=nickname,
        first_name=first_name,
        last_name=last_name,
        permissions=0
    )

    # Работаем с базой данных
    async with AsyncSessionLocal() as session:
        # Проверяем, существует ли пользователь
        result = await session.execute(select(User).where(User.user_id == user_id))
        existing_user = result.scalars().first()

        if not existing_user:
            # Если пользователь новый, добавляем его в базу данных
            session.add(new_user)
        else:
            # Если пользователь существует, обновляем его данные
            existing_user.nicname = nickname
            existing_user.first_name = first_name
            existing_user.last_name = last_name

        # Сохраняем изменения в базе данных
        await session.commit()

    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)





@router.message(F.text == "Меню")
async def menu(msg: Message):
    user_id = msg.from_user.id

    if await is_gromozeka(user_id):
        await msg.answer(gromozeka)
        return
    await msg.answer(text.menu, reply_markup=kb.menu)

@router.message(F.text == "Мой профиль 📂")
async def profile_handler(message: types.Message):
    user_id = message.from_user.id

    if await is_gromozeka(user_id):
        await message.answer(gromozeka)
        return
    await message.answer("Выберите действие:", reply_markup=kb.user_menu)
    
@router.message(F.text == "Инфо🧾")
async def info_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.first_name

    if await is_gromozeka(user_id):
        await message.answer(gromozeka)
        return

    # Работа с базой данных
    async with AsyncSessionLocal() as session:
        # Получаем данные о пользователе
        result = await session.execute(select(User).where(User.user_id == user_id))
        user_info = result.scalars().first()

        if not user_info:
            await message.answer("Пользователь не найден.")
            return

        # Подсчитаем количество оценок пользователя
        result = await session.execute(select(Rating).where(Rating.user_id == user_id))
        user_ratings = result.scalars().all()

        # Количество оценок
        num_votes = len(user_ratings)

    # Отправка сообщения с информацией о пользователе
    await message.answer(f"Имя: {username}\nКоличество оценок: {num_votes}⭐️")

@router.message(F.text == "Список мест 🏘")
async def places_handler(message: types.Message):
    user_id = message.from_user.id

    if await is_gromozeka(user_id):
        await message.answer(gromozeka)
        return

    async with AsyncSessionLocal() as session:
        # Получаем все места из базы данных
        result = await session.execute(select(Place))
        places = result.scalars().all()

        if not places:
            await message.answer("Места не найдены.")
            return

        # Создание кнопок для каждого места
        buttons = [
            [InlineKeyboardButton(text=place.place_name, callback_data=f"place_{place.place_id}")]
            for place in places
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer("Список мест:", reply_markup=markup)

@router.callback_query(F.data.startswith("place_"))
async def place_callback_handler(cq: CallbackQuery):
    try:
        # Извлеките place_id из данных обратного вызова
        place_id = int(cq.data.split("_")[1])

        async with AsyncSessionLocal() as session:
            # Получаем место по place_id
            result = await session.execute(select(Place).where(Place.place_id == place_id))
            place = result.scalars().first()

            if not place:
                await cq.message.answer(f"Место с ID {place_id} не найдено.")
                return

            # Получаем список пив, доступных в этом месте через таблицу place_beers
            result = await session.execute(select(Beer).join(PlaceBeer).where(PlaceBeer.place_id == place_id))
            beers_in_place = result.scalars().all()

            if not beers_in_place:
                await cq.message.answer(f"В месте {place.place_name} нет доступного пива.")
                return

            # Создание кнопок для каждого пива
            buttons = [
                [InlineKeyboardButton(text=beer.name, callback_data=f"beer_{beer.beer_id}")]
                for beer in beers_in_place
            ]
            markup = InlineKeyboardMarkup(inline_keyboard=buttons)

            await cq.message.answer(f"Место: {place.place_name}\nПиво:", reply_markup=markup)

    except Exception as e:
        await cq.message.answer(f"Произошла ошибка: {e}")

@router.callback_query(F.data.startswith("beer_"))
async def beer_callback_handler(cq: CallbackQuery):
    try:
        # Извлеките идентификатор пива из данных обратного вызова
        beer_id = int(cq.data.split("_")[1])

        async with AsyncSessionLocal() as session:
            # Найдите пиво в базе данных
            result = await session.execute(select(Beer).where(Beer.beer_id == beer_id))
            selected_beer = result.scalars().first()

            if selected_beer is None:
                await cq.message.answer("Произошла ошибка: пиво не найдено.")
                return

            # Создайте клавиатуру с кнопками для оценки пива от 1 до 5
            buttons = [
                [InlineKeyboardButton(text="1️⃣", callback_data=f"rate_1_{beer_id}"),
                 InlineKeyboardButton(text="2️⃣", callback_data=f"rate_2_{beer_id}"),
                 InlineKeyboardButton(text="3️⃣", callback_data=f"rate_3_{beer_id}"),
                 InlineKeyboardButton(text="4️⃣", callback_data=f"rate_4_{beer_id}"),
                 InlineKeyboardButton(text="5️⃣", callback_data=f"rate_5_{beer_id}")]
            ]
            markup = InlineKeyboardMarkup(inline_keyboard=buttons)

            # Отправьте сообщение с названием выбранного пива и клавиатурой для рейтинга
            await cq.message.answer(f"Вы выбрали: {selected_beer.name}\nПоставьте оценку от 1 до 5:", reply_markup=markup)

    except Exception as e:
        await cq.message.answer(f"Произошла ошибка: {e}")

@router.callback_query(F.data.startswith("rate_"))
async def rate_callback_handler(cq: CallbackQuery):
    try:
        # Извлекаем оценку и идентификатор пива из данных обратного вызова
        rating_value = int(cq.data.split("_")[1])
        beer_id = int(cq.data.split("_")[2])
        user_id = cq.from_user.id

        async with AsyncSessionLocal() as session:
            # Проверка на существование записи рейтинга для этого пива и пользователя
            result = await session.execute(select(Rating).where(Rating.user_id == user_id, Rating.beer_id == beer_id))
            existing_rating = result.scalars().first()

            if existing_rating:
                # Если рейтинг уже существует, обновляем его
                existing_rating.rating = rating_value
            else:
                # Если рейтинга нет, создаем новую запись
                new_rating = Rating(user_id=user_id, beer_id=beer_id, rating=rating_value)
                session.add(new_rating)

            # Сохраняем изменения в базе данных
            await session.commit()

        # Отправляем подтверждение пользователю
        await cq.message.answer(f"Спасибо! Ваша оценка — {rating_value} ⭐️")

    except Exception as e:
        await cq.message.answer(f"Произошла ошибка при сохранении вашей оценки: {e}")


@router.callback_query(F.data.startswith("rate_"))
async def rate_callback_handler(cq: CallbackQuery):
    try:
        # Извлекаем оценку и идентификатор пива из данных обратного вызова
        rating_value = int(cq.data.split("_")[1])
        beer_id = int(cq.data.split("_")[2])
        user_id = cq.from_user.id

        async with AsyncSessionLocal() as session:
            # Проверка на существование записи рейтинга для этого пива и пользователя
            result = await session.execute(select(Rating).where(Rating.user_id == user_id, Rating.beer_id == beer_id))
            existing_rating = result.scalars().first()

            if existing_rating:
                # Если рейтинг уже существует, обновляем его
                existing_rating.rating = rating_value
            else:
                # Если рейтинга нет, создаем новую запись
                new_rating = Rating(user_id=user_id, beer_id=beer_id, rating=rating_value)
                session.add(new_rating)

            # Сохраняем изменения в базе данных
            await session.commit()

        # Отправляем подтверждение пользователю
        await cq.message.answer(f"Спасибо! Ваша оценка — {rating_value} ⭐️")

    except Exception as e:
        await cq.message.answer(f"Произошла ошибка при сохранении вашей оценки: {e}")


@router.message(F.text == "Мои оценки⭐️")
async def handle_user_ratings(message: types.Message, state: FSMContext):
    try:
        user_id = message.from_user.id

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Beer, Rating.rating)
                .join(Rating, Rating.beer_id == Beer.beer_id)
                .where(Rating.user_id == user_id)
            )
            user_ratings = result.all()

        if not user_ratings:
            await message.answer("Вы еще не поставили ни одной оценки.")
            return

        # Сохраните оценки пользователя в состоянии
        await state.update_data(user_ratings=user_ratings, rating_page=1)

        # Отображаем первую страницу оценок
        await display_user_ratings(message, user_ratings, 1)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")


async def display_user_ratings(message: types.Message, user_ratings, page, is_new_message=False):
    start = (page - 1) * 10
    end = start + 10
    page_items = user_ratings[start:end]

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{beer.name} / {beer.brewery} - {rating} ⭐️",
                callback_data=f"item_{beer.beer_id}"
            )
        ]
        for beer, rating in page_items
    ]

    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"rating_page:{page - 1}"))
    if end < len(user_ratings):
        navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"rating_page:{page + 1}"))

    if navigation_buttons:
        buttons.append(navigation_buttons)

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    try:
        if is_new_message:
            # Отправляем новое сообщение
            await message.answer("Ваши оценки:", reply_markup=markup)
        else:
            # Редактируем сообщение
            await message.edit_text("Ваши оценки:", reply_markup=markup)
    except TelegramBadRequest as e:
        if "can't be edited" in str(e):
            # Если сообщение нельзя редактировать, отправляем новое
            await message.answer("Ваши оценки:", reply_markup=markup)
        else:
            raise



@router.callback_query(F.data.startswith("rating_page:"))
async def rating_page_callback_handler(cq: CallbackQuery, state: FSMContext):
    try:
        # Получаем данные о текущих оценках и странице из состояния
        data = await state.get_data()
        user_ratings = data.get("user_ratings", [])
        page = int(cq.data.split(":")[1])

        # Обновляем сообщение с оценками
        await display_user_ratings(cq.message, user_ratings, page)

        # Обновляем текущую страницу в состоянии
        await state.update_data(rating_page=page)
    except Exception as e:
        await cq.answer(f"Произошла ошибка: {e}", show_alert=True)



@router.message(F.text.lower() == "вернуться в меню")
async def search_handler(message: types.Message, state: FSMContext):
    await message.answer("Возвращаемся в меню...", reply_markup=kb.menu)
    await state.clear()


@router.callback_query(F.data.startswith("item_"))
async def item_callback_handler(cq: CallbackQuery):
    try:
        # Извлеките идентификатор пива из данных обратного вызова
        beer_id = int(cq.data.split("_")[1])

        # Найдите пиво в списке пива
        beer_list = await load_beer_list()
        selected_beer = next((beer for beer in beer_list if beer['id'] == beer_id), None)

        if selected_beer is None:
            await cq.message.answer("Произошла ошибка: пиво не найдено.")
            return

        # Создайте клавиатуру с кнопками 1, 2, 3, 4, 5 для оценки пива
        buttons = [
            [InlineKeyboardButton(text="1️⃣", callback_data=f"rate_1_{beer_id}"),
             InlineKeyboardButton(text="2️⃣", callback_data=f"rate_2_{beer_id}"),
             InlineKeyboardButton(text="3️⃣", callback_data=f"rate_3_{beer_id}"),
             InlineKeyboardButton(text="4️⃣", callback_data=f"rate_4_{beer_id}"),
             InlineKeyboardButton(text="5️⃣", callback_data=f"rate_5_{beer_id}")]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        # Отправьте сообщение с названием выбранного пива и клавиатурой
        await cq.message.answer(f"Вы выбрали: {selected_beer['name']}\nОцените это пиво:", reply_markup=markup)

    except Exception as e:
        await cq.message.answer(f"Произошла ошибка: {e}")

##############################################################################################################################################

class SearchState(StatesGroup):
    WaitingForBeerQuery = State()
    WaitingForBreweryQuery = State()


@router.message(F.text == "Поиск 🔍")
async def search_handler(message: types.Message):
    user_id = message.from_user.id

    if await is_gromozeka(user_id):
        await message.answer(gromozeka)
        return
    await message.answer("Выберите тип поиска:", reply_markup=kb.search_menu)

@router.message(F.text == "Поиск по пивоварням")
async def search_brewery_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if await is_gromozeka(user_id):
        await message.answer(gromozeka)
        return

    try:
        await message.answer("Введите название пивоварни, которую вы ищете:")
        await state.set_state(SearchState.WaitingForBreweryQuery.state)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

@router.message(F.text == "Поиск по пиву")
async def search_beer_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if await is_gromozeka(user_id):
        await message.answer(gromozeka)
        return

    try:
        await message.answer("Введите название пива, которое вы ищете:")
        await state.set_state(SearchState.WaitingForBeerQuery.state)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

@router.message(F.text.lower() == "вернуться в меню")
async def search_handler(message: types.Message, state: FSMContext):
    await message.answer("Возвращаемся в меню...", reply_markup=kb.menu)
    await state.clear()


async def get_search_results(query: str, search_function, page: int):
    # Выполняем поиск
    search_results = await search_function(query)

    if not search_results:
        return None, "К сожалению, по вашему запросу ничего не найдено."

    # Генерация кнопок с результатами поиска
    start = (page - 1) * 10
    end = start + 10
    page_items = search_results[start:end]

    buttons = [
        [InlineKeyboardButton(text=f"{item['name']} / ({item['brewery']})", callback_data=f"item_{item['id']}")]
        for item in page_items
    ]

    # Навигационные кнопки
    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"search_results:{page - 1}"))
    if end < len(search_results):
        navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"search_results:{page + 1}"))

    if navigation_buttons:
        buttons.append(navigation_buttons)

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup, None  # Возвращаем кнопки и ошибку (если есть)



@router.message(SearchState.WaitingForBeerQuery)
async def get_search_results_beer(message: types.Message, state: FSMContext):
    try:
        search_query = message.text
        search_results = await search_by_beer(search_query)  # Выполняем поиск

        if not search_results:
            await message.answer("К сожалению, по вашему запросу ничего не найдено.")
            return

        # Сохраняем результаты поиска в состояние
        await state.update_data(search_results=search_results)

        page = 1  # Начальная страница
        markup, error = await get_search_results_for_page(state, page)

        if error:
            await message.answer(error)
            return

        await message.answer("Результаты поиска:", reply_markup=markup)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

async def get_search_results_for_page(state: FSMContext, page: int):
    """Генерация кнопок для указанной страницы из сохранённых результатов."""
    data = await state.get_data()
    search_results = data.get("search_results", [])

    if not search_results:
        return None, "К сожалению, результаты поиска отсутствуют."

    # Генерация кнопок для текущей страницы
    start = (page - 1) * 10
    end = start + 10
    page_items = search_results[start:end]

    buttons = [
        [InlineKeyboardButton(text=f"{item['name']} / ({item['brewery']})", callback_data=f"item_{item['id']}")]
        for item in page_items
    ]

    # Навигационные кнопки
    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"search_results:{page - 1}"))
    if end < len(search_results):
        navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"search_results:{page + 1}"))

    if navigation_buttons:
        buttons.append(navigation_buttons)

    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup, None

@router.callback_query(F.data.startswith("search_results:"))
async def search_results_callback_handler(cq: CallbackQuery, state: FSMContext):
    try:
        page = int(cq.data.split(":")[1])  # Получаем номер страницы

        # Получаем результаты для указанной страницы
        markup, error = await get_search_results_for_page(state, page)

        if error:
            await cq.answer(error)
            return

        # Обновляем сообщение
        await cq.message.edit_text("Результаты поиска:", reply_markup=markup)
    except Exception as e:
        await cq.answer(f"Произошла ошибка: {e}")



@router.message(SearchState.WaitingForBreweryQuery)
async def get_search_results_breweries(message: types.Message, state: FSMContext):
    try:
        search_query = message.text
        # Выполняем поиск
        search_results = await search_by_breweries(search_query)

        if not search_results:
            await message.answer("К сожалению, по вашему запросу ничего не найдено.")
            return

        # Сохраняем результаты поиска в состояние
        await state.update_data(search_results=search_results)

        page = 1  # Начальная страница
        markup, error = await get_search_results_for_page(state, page)

        if error:
            await message.answer(error)
            return

        await message.answer("Результаты поиска пивоварен:", reply_markup=markup)
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

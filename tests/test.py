from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from sqlalchemy.future import select

@router.callback_query(F.data.startswith("page:"))
async def page_callback_handler(cq: CallbackQuery, state: FSMContext):
    try:
        # Извлеките номер страницы из данных обратного вызова
        page = int(cq.data.split(":")[1])

        user_id = cq.from_user.id

        # Загрузим данные оценок из базы данных
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Rating).where(Rating.user_id == user_id))
            user_ratings = result.scalars().all()

        # Загружаем список пив
        beer_list = await load_beer_list()

        # Преобразуем список пив и оценок в словарь с ID пива и оценкой
        beer_ratings = {rating.beer_id: rating.rating for rating in user_ratings}

        # Создаем список пив с их оценками
        all_beers = []
        for beer in beer_list:
            rating = beer_ratings.get(beer['id'], None)  # Получаем оценку пива, если она есть
            beer_info = {
                "id": beer['id'],
                "name": beer['name'],
                "brewery": beer['brewery'],
                "rating": rating if rating is не None else "Не оценено"
            }
            all_beers.append(beer_info)

        # Определяем, какие элементы отображать на текущей странице
        start = (page - 1) * 10
        end = start + 10
        page_items = all_beers[start:end]

        # Генерация кнопок с отображением оценки
        buttons = [
            [
                InlineKeyboardButton(
                    text=f"{item['name']} / {item['brewery']} / Оценка: {item['rating']}",
                    callback_data=f"item_{item['id']}"
                )
            ]
            for item in page_items
        ]

        # Навигационные кнопки для перехода между страницами
        navigation_buttons = []
        if page > 1:
            navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page:{page - 1}"))
        if end < len(all_beers):
            navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"page:{page + 1}"))

        if navigation_buttons:
            buttons.append(navigation_buttons)

        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        await cq.message.edit_text("Ваши оценки:", reply_markup=markup)

        # Обновляем текущую страницу в состоянии
        await state.update_data(search_page=page)

    except Exception as e:
        await cq.answer(f"Произошла ошибка: {e}")

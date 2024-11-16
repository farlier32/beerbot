from aiogram.types.callback_query import CallbackQuery
from utils.db_loader import load_beer_list
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.votes import update_vote_results

async def handle_beer_selection(cq: CallbackQuery, beer_id: int):
    try:
        # Поиск пива по выбранному id
        beer_list = load_beer_list()
        selected_beer = next((beer for beer in beer_list if beer['id'] == beer_id), None)
        
        if selected_beer is None:
            await cq.message.answer("Произошла ошибка: пиво не найдено.")
            return

        # Создание клавиатуры с кнопками "Нравится" и "Не нравится"
        buttons = [
            [InlineKeyboardButton(text="👍", callback_data=f"like_{beer_id}"),
            InlineKeyboardButton(text="👎", callback_data=f"dislike_{beer_id}")]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)

        # Отправка сообщение с названием выбранного пива и клавиатурой
        await cq.message.answer(f"Вы выбрали: {selected_beer['name']}", reply_markup=markup)

    except Exception as e:
        await cq.message.answer(f"Произошла ошибка: {e}")

async def update_vote_and_respond(cq: CallbackQuery, beer_id: int, vote: str):
    user_id = cq.from_user.id

    # Поиск пива по выбранному id
    beer_list = load_beer_list()
    selected_beer = next((beer for beer in beer_list if beer['id'] == beer_id), None)
    
    if selected_beer is None:
        await cq.message.answer("Произошла ошибка: пиво не найдено.")
        return

    # Обновление голоса
    update_vote_results(user_id, selected_beer['id'], vote)

    await cq.answer("Ваш голос учтен!")
    await cq.message.delete()


async def handle_exception(cq: CallbackQuery, e: Exception):
    await cq.answer(f"Произошла ошибка: {e}")



from aiogram.types import InlineKeyboardButton
import json


def load_votes(user_id):
    with open('data/votes.json', 'r', encoding='utf8') as f:
        vote_data = json.load(f)
    user_votes = vote_data.get(str(user_id), {})
    liked_beers_ids = [int(beer_id) for beer_id, vote in user_votes.items() if vote == "like"]
    disliked_beers_ids = [int(beer_id) for beer_id, vote in user_votes.items() if vote == "dislike"]
    return liked_beers_ids, disliked_beers_ids

def generate_buttons(items, current_page, total_items, callback_prefix, user_id=None, update_votes=False, page_prefix=''):
    buttons = []
    liked_beers_ids, disliked_beers_ids = [], []  # Определите переменные здесь
    if update_votes and user_id is not None:
        liked_beers_ids, disliked_beers_ids = load_votes(user_id)  # Обновите переменные здесь
    for item in items:
        if isinstance(item, dict):
            # Если элемент является словарем, используем поля 'name' и 'brewery'
            text = f"{item['name']} / {item['brewery']}"
            callback_data = f"{callback_prefix}_{item['id']}"
            if item['id'] in liked_beers_ids:
                text = f"👍 {text}"
            elif item['id'] in disliked_beers_ids:
                text = f"👎 {text}"
        else:
            # Если элемент является строкой, используем её напрямую
            text = item
            callback_data = f"{callback_prefix}_{item}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    navigation_buttons = []
    if current_page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"{page_prefix}:{current_page - 1}"))
    if (current_page - 1) * 10 + len(items) < total_items:
        navigation_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"{page_prefix}:{current_page + 1}"))
    if navigation_buttons:
        buttons.append(navigation_buttons)
    return buttons

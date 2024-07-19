import json
from aiogram.types import Message
from aiogram import BaseMiddleware


def check_permissions(user_id: int, required_permission: int):
    with open('data/users.json', 'r', encoding='utf8') as f:
        user_data = json.load(f)
        user_info = next((user for user in user_data['users'] if user['id'] == user_id), None)

    if user_info is None or user_info['permissions'] < required_permission or user_info['permissions'] == 228:
        return False

    return True

def is_gromozeka(user_id: int) -> bool:
    with open('data/users.json', 'r', encoding='utf8') as f:
        users = json.load(f)
        user_info = next((user for user in users['users'] if user['id'] == user_id), None)

    return user_info is not None and user_info['permissions'] == 228

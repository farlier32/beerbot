from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)

menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Поиск 🔍")
        ],
        [
            KeyboardButton(text="Список мест 🏘"),
            KeyboardButton(text="Мой профиль 📂")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие из меню",
    selective=True
)
search_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Поиск по пивоварням"),
            KeyboardButton(text="Поиск по пиву")
        ],
        [
            KeyboardButton(text="Вернуться в меню")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие из меню",
    selective=True
)

user_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Мои оценки⭐️"),
            KeyboardButton(text="Инфо🧾")
        ],
        [
            KeyboardButton(text="Вернуться в меню")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие из меню",
    selective=True
)


admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить место"),
            KeyboardButton(text="Команды")
        ],
        [
            KeyboardButton(text="Вернуться в меню")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие из меню",
    selective=True
)

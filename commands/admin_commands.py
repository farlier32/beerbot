from aiogram import types, F, Router
from utils.db_loader import load_beer_list
from aiogram.types import Message
from aiogram.filters.state import State, StatesGroup
from utils.permissions import check_permissions
from aiogram.filters import Command
from keyboards.reply import admin_menu
from aiogram.fsm.context import FSMContext
import json
router = Router()

class AdminState(StatesGroup):
    WaitingForUsername = State()
    WaitingForUsernamePermission = State()
    WaitingForId = State()
    WaitingForPermission = State()



@router.message(F.text == 'Команды')
async def admin_commands(message: types.Message):
    try:
        user_id = message.from_user.id
        has_permission = check_permissions(user_id, 1)

        if not has_permission:
            await message.answer("Извините, но у вас не хватает прав.")
            return
        await message.answer('Команды:\n/userinfo - Получить данные о пользователе по @nick.\n/change_permission - Назначение ролей.')
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")


@router.message(Command("admin"))
async def add_beer_place_handler(message: types.Message):
    try:
        user_id = message.from_user.id
        has_permission = check_permissions(user_id, 1)

        if not has_permission:
            await message.answer("Извините, но у вас не хватает прав.")
            return

        await message.answer("КРэК", reply_markup=admin_menu)
        return

    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")


@router.message(Command("userinfo"))
async def user_info_start(message: types.Message, state: FSMContext):
    # Проверка разрешений, как в команде admin
    user_id = message.from_user.id
    has_permission = check_permissions(user_id, 1)

    if not has_permission:
        await message.answer("Извините, но у вас не хватает прав.")
        return

    await message.answer("Введите никнейм пользователя:")
    await state.set_state(AdminState.WaitingForUsername.state)


@router.message(AdminState.WaitingForUsername)
async def user_info(message: types.Message, state: FSMContext):
    username = message.text.lstrip('@')

    # Загрузка данных пользователя из users.json
    with open('data/users.json', 'r', encoding='utf8') as f:
        user_data = json.load(f)
        user_info = next((user for user in user_data['users'] if user['nick'] == username), None)

    if user_info is None:
        await message.answer("Пользователь не найден.")
        return

    # Загрузка данных оценок из votes.json
    with open('data/votes.json', 'r', encoding='utf8') as f:
        vote_data = json.load(f)
        user_votes = vote_data.get(str(user_info['id']), {})
        liked_beers_ids = [int(beer_id) for beer_id, vote in user_votes.items() if vote == "like"]
        disliked_beers_ids = [int(beer_id) for beer_id, vote in user_votes.items() if vote == "dislike"]

    info = f"""
    ID: {user_info['id']}
    Ник: {user_info['nick']}
    Имя: {user_info['name']}
    Фамилия: {user_info['last_name']}
    Права доступа: {user_info['permissions']}
    Количество лайкнутых пив: {len(liked_beers_ids)}
    Количество дизлайкнутых пив: {len(disliked_beers_ids)}
    """

    await message.answer(info)
    await state.clear()

@router.message(Command("change_permission"))
async def change_permission_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    has_permission = check_permissions(user_id, 2)

    if not has_permission:
        await message.answer("Извините, но у вас не хватает прав.")
        return

    await message.answer("Введите никнейм пользователя:")
    await state.set_state(AdminState.WaitingForUsernamePermission.state)

@router.message(AdminState.WaitingForUsernamePermission)
async def change_permission_username(message: types.Message, state: FSMContext):
    nick = message.text.lstrip('@')
    await state.update_data(nick=nick)
    await message.answer("Введите новое разрешение для пользователя:\n0 - Default,\n1 - Moderator,\n2 - Administration,\n228 - GROMOZEKA BANNED")
    await state.set_state(AdminState.WaitingForPermission.state)


immutable_users = [1021919114]
@router.message(AdminState.WaitingForPermission)
async def change_permission_finish(message: types.Message, state: FSMContext):
    new_permission = int(message.text)
    user_data = await state.get_data()
    nick = user_data['nick']

    # Загрузка данных пользователя из users.json
    with open('data/users.json', 'r', encoding='utf8') as f:
        users = json.load(f)
        user_info = next((user for user in users['users'] if user.get('nick') == nick), None)

    if user_info is None:
        await message.answer("Пользователь не найден.")
        await state.clear()
        return

    # Проверка, является ли пользователь неизменяемым
    if user_info['id'] in immutable_users:
        await message.answer("Извините, но разрешения этого пользователя не могут быть изменены.")
        await state.clear()
        return

    # Изменение разрешения пользователя
    user_info['permissions'] = new_permission

    # Сохранение обновленных данных пользователя в users.json
    with open('data/users.json', 'w', encoding='utf8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

    await message.answer(f"Разрешение для пользователя {nick} успешно изменено на {new_permission}.")
    await state.clear()


class AddPlaceState(StatesGroup):
    WaitingForPlaceName = State()
    WaitingForBeerNames = State()

@router.message(F.text.lower() == "добавить место")
async def add_place_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    has_permission = check_permissions(user_id, 2)

    if not has_permission:
        await message.answer("Извините, но у вас не хватает прав.")
        return

    await message.answer("Введите название места:")
    await state.set_state(AddPlaceState.WaitingForPlaceName.state)

@router.message(F.text, AddPlaceState.WaitingForPlaceName)
async def add_place_name(message: types.Message, state: FSMContext):
    place_name = message.text
    await state.update_data(place_name=place_name)
    await message.answer("Введите названия пив, которые сейчас в продаже. Когда закончите, введите /create_place.")
    await state.set_state(AddPlaceState.WaitingForBeerNames.state)

@router.message(F.text, AddPlaceState.WaitingForBeerNames)
async def add_place_beer_names(message: types.Message, state: FSMContext):
    if message.text == "/create_place":
        data = await state.get_data()
        place_name = data.get("place_name")
        beer_names = data.get("beer_names", [])
        
        beer_list = await load_beer_list()
        beer_ids = [beer['id'] for beer in beer_list if beer['name'] in beer_names]

        place_info = {"beers": beer_ids}

        with open('data/places.json', 'r', encoding='utf8') as f:
            places = json.load(f)

        places[place_name] = place_info

        with open('data/places.json', 'w', encoding='utf8') as f:
            json.dump(places, f, ensure_ascii=False, indent=2)

        await message.answer(f"Место {place_name} успешно добавлено.")
        await state.clear()
    else:
        # Добавьте введенное пользователем название пива в список
        await state.update_data(beer_names=message.text.split(", "))

# @router.message(Command("dbupdate"))
# async def database_update(message: types.Message, state: FSMContext):
#     user_id = message.from_user.id
#     has_permission = check_permissions(user_id, 2)

#     if not has_permission:
#         await message.answer("Извините, но у вас не хватает прав.")
#         return
#     else:

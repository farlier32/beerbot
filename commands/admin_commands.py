from aiogram import types, F, Router
from aiogram.filters.state import State, StatesGroup
from utils.permissions import check_permissions
from aiogram.filters import Command
from keyboards.reply import admin_menu
from aiogram.fsm.context import FSMContext

from sqlalchemy.future import select
from db.database import AsyncSessionLocal
from db.models import *






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
        has_permission = await check_permissions(user_id, 1)

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
        has_permission = await check_permissions(user_id, 1)

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
    has_permission = await check_permissions(user_id, 1)

    if not has_permission:
        await message.answer("Извините, но у вас не хватает прав.")
        return

    await message.answer("Введите никнейм пользователя:")
    await state.set_state(AdminState.WaitingForUsername.state)


@router.message(AdminState.WaitingForUsername)
async def user_info(message: types.Message, state: FSMContext):
    username = message.text.lstrip('@')

    # Работаем с базой данных
    async with AsyncSessionLocal() as session:
        # Получаем пользователя по никнейму
        result = await session.execute(select(User).where(User.nickname == username))
        user_info = result.scalars().first()

        if user_info is None:
            await message.answer("Пользователь не найден.")
            return

        # Получаем все оценки пользователя
        result = await session.execute(select(Rating).where(Rating.user_id == user_info.user_id))
        user_votes = result.scalars().all()

    # Формируем информацию о пользователе
    info = f"""
    ID: {user_info.user_id}
    Ник: {user_info.nickname}
    Имя: {user_info.first_name}
    Фамилия: {user_info.last_name}
    Права доступа: {user_info.permissions}
    Количество оценок: {len(user_votes)}
    """

    await message.answer(info)
    await state.clear()


@router.message(Command("change_permission"))
async def change_permission_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    # Проверяем, есть ли у пользователя права для выполнения этой команды
    has_permission = await check_permissions(user_id, 2)

    if not has_permission:
        await message.answer("Извините, но у вас не хватает прав.")
        return

    # Запрашиваем никнейм пользователя, чьи права нужно изменить
    await message.answer("Введите никнейм пользователя:")
    await state.set_state(AdminState.WaitingForUsernamePermission.state)


@router.message(AdminState.WaitingForUsernamePermission)
async def change_permission_username(message: types.Message, state: FSMContext):
    # Извлекаем никнейм пользователя
    nickname = message.text.lstrip('@')
    await state.update_data(nickname=nickname)

    # Запрашиваем новое разрешение для пользователя
    await message.answer(
        "Введите новое разрешение для пользователя:\n0 - Default,\n1 - Moderator,\n2 - Administration,\n228 - GROMOZEKA BANNED")
    await state.set_state(AdminState.WaitingForPermission.state)


immutable_users = [1021919114]
@router.message(AdminState.WaitingForPermission)
async def change_permission_finish(message: types.Message, state: FSMContext):
    try:
        new_permission = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение для прав доступа.")
        return

    user_data = await state.get_data()
    nickname = user_data.get('nickname')

    # Работаем с базой данных
    async with AsyncSessionLocal() as session:
        # Выполняем запрос на получение пользователя с данным никнеймом
        result = await session.execute(select(User).where(User.nickname == nickname))
        user_info = result.scalars().first()

        if user_info is None:
            await message.answer("Пользователь не найден.")
            await state.clear()
            return

        # Проверка, является ли пользователь неизменяемым
        if user_info.user_id in immutable_users:
            await message.answer("Извините, но разрешения этого пользователя не могут быть изменены.")
            await state.clear()
            return

        # Обновляем права пользователя
        user_info.permissions = new_permission
        await session.commit()

    await message.answer(f"Права доступа пользователя {nickname} успешно изменены на {new_permission}.")
    await state.clear()


class AddPlaceState(StatesGroup):
    WaitingForPlaceName = State()
    WaitingForBeerNames = State()


@router.message(F.text.lower() == "добавить место")
async def add_place_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    has_permission = await check_permissions(user_id, 2)

    if not has_permission:
        await message.answer("Извините, но у вас не хватает прав.")
        return

    await message.answer("Введите название места:")
    await state.set_state(AddPlaceState.WaitingForPlaceName.state)


# Добавление названия места
@router.message(F.text, AddPlaceState.WaitingForPlaceName)
async def add_place_name(message: types.Message, state: FSMContext):
    place_name = message.text
    await state.update_data(place_name=place_name)
    await message.answer("Введите названия пив, которые сейчас в продаже. Когда закончите, введите /create_place.")
    await state.set_state(AddPlaceState.WaitingForBeerNames.state)


# Добавление пив в место и сохранение в базе данных
@router.message(F.text, AddPlaceState.WaitingForBeerNames)
async def add_place_beer_names(message: types.Message, state: FSMContext):
    if message.text == "/create_place":
        data = await state.get_data()
        place_name = data.get("place_name")
        beer_names = data.get("beer_names", [])

        # Получаем список пива из базы данных
        async with AsyncSessionLocal() as session:
            beer_list = await session.execute(select(Beer).filter(Beer.name.in_(beer_names)))
            beers = beer_list.scalars().all()
            beer_ids = [beer.beer_id for beer in beers]

            if not beer_ids:
                await message.answer("Не найдено пива с указанными названиями.")
                await state.clear()
                return

            # Создание нового места в базе данных
            new_place = Place(place_name=place_name)
            session.add(new_place)
            await session.commit()

            # Добавление связи между местом и пивом в таблицу place_beers
            for beer_id in beer_ids:
                place_beer = PlaceBeer(place_id=new_place.place_id, beer_id=beer_id)
                session.add(place_beer)

            await session.commit()

        await message.answer(f"Место {place_name} успешно добавлено.")
        await state.clear()
    else:
        # Добавляем введенные названия пива в список
        beer_names = message.text.split(", ")
        await state.update_data(beer_names=beer_names)

# @router.message(Command("dbupdate"))
# async def database_update(message: types.Message, state: FSMContext):
#     user_id = message.from_user.id
#     has_permission = check_permissions(user_id, 2)

#     if not has_permission:
#         await message.answer("Извините, но у вас не хватает прав.")
#         return
#     else:

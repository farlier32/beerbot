@router.message(F.text.lower() == "добавить место")
async def start_add_place(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    has_permission = check_permissions(user_id, 2)

    if not has_permission:
        await message.answer("Извините, но у вас не хватает прав.")
        return

    await message.answer("Введите название места.")
    await state.set_state(AddPlaceState.WaitingForPlaceName.state)

@router.message(AddPlaceState.WaitingForPlaceName)
async def add_place_name(message: types.Message, state: FSMContext):
    place_name = message.text
    await state.update_data(place_name=place_name)
    await message.answer("Введите запрос для поиска пива.")
    await state.set_state(AddPlaceState.WaitingForBeerNames.state)

@router.message(AddPlaceState.WaitingForBeerNames)
async def search_beer(message: types.Message, state: FSMContext):
    if message.text == "/create_place":
        data = await state.get_data()
        place_name = data.get("place_name")
        beer_ids = data.get("beer_ids", [])
        place_info = {"beers": beer_ids}
        with open('data/places.json', 'r', encoding='utf8') as f:
            places = json.load(f)
        places[place_name] = place_info
        with open('data/places.json', 'w', encoding='utf8') as f:
            json.dump(places, f, ensure_ascii=False, indent=2)
        await message.answer(f"Место {place_name} успешно добавлено.")
        await state.clear()
    else:
        search_query = message.text
        search_results = search_by_beer(search_query)
        buttons = [[InlineKeyboardButton(text=f"{beer['name']} / ({beer['brewery']})", callback_data=f"beer_{beer['id']}")] for beer in search_results]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer("Результаты поиска:", reply_markup=markup)

@router.callback_query(F.callback_data.filter(prefix="beer_"), AddPlaceState.WaitingForBeerNames)
async def select_beer(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    beer_id = callback_data["id"]
    data = await state.get_data()
    beer_ids = data.get("beer_ids", [])
    beer_ids.append(beer_id)
    await state.update_data(beer_ids=beer_ids)
    await callback_query.answer(f"Пиво {beer_id} добавлено.")
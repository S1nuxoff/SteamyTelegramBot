from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from typing import Union
import aiohttp

from app.utils.errors import get_error_message

from app.keyboards import (
    inspect_menu,
    setup_inspect_mode,
    game,
    back,
    favorite_items_list,
)
from app.states.states import SetupItemToInspect

import app.database.requests as rq
from app.utils.localization import get_text

inspect_menu_router = Router()


async def item_setup(target: Union[CallbackQuery, Message], sel_game_data, user_language, state: FSMContext):
    # Store users language in the state
    await state.update_data(user_language=user_language)

    keyboard = await setup_inspect_mode(user_language)
    game_name = sel_game_data.get("name", "Unknown Game")
    text = get_text(user_language, 'inspect_menu.INSPECT_ITEM_MENU').format(game_name=game_name)

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(
            text=text, parse_mode="Markdown", reply_markup=keyboard
        )
        await target.answer()
    elif isinstance(target, Message):
        await target.answer(text=text, parse_mode="Markdown", reply_markup=keyboard)

    await state.set_state(SetupItemToInspect.item_name)


async def show_inspect_menu(target: Union[CallbackQuery, Message], state: FSMContext):
    user_id = target.from_user.id
    user_data = await rq.get_state(user_id)
    sel_game_data = user_data.get("sel_game_data")
    inspected_item = user_data.get("inspected_item")

    # Retrieve user_language from the state
    state_data = await state.get_data()
    user_language = state_data.get('user_language', user_data.get('language'))  # Fallback to user_data if not in state

    if inspected_item is None:
        await item_setup(target, sel_game_data, user_language, state)
    else:
        keyboard = await inspect_menu(user_language)
        text = get_text(user_language, 'inspect_menu.CURRENTLY_INSPECTING_ITEM').format(inspected_item=inspected_item)

        if isinstance(target, CallbackQuery):
            await target.message.edit_text(
                text=text, parse_mode="Markdown", reply_markup=keyboard
            )
            await target.answer()
        elif isinstance(target, Message):
            await target.answer(text=text, parse_mode="Markdown", reply_markup=keyboard)


@inspect_menu_router.message(SetupItemToInspect.item_name)
async def handle_item_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await rq.get_state(user_id)
    sel_game_data = user_data.get("sel_game_data")
    appid = sel_game_data.get('steam_id')
    item_name = message.text.strip()

    # Retrieve user_language from the state
    state_data = await state.get_data()
    user_language = state_data.get('user_language', user_data.get('language'))

    API_URL = "http://185.93.6.180:8000/verify_item"

    async with aiohttp.ClientSession() as session:
        async with session.get(
                API_URL,
                params={"appid": appid, "items": item_name}
        ) as response:
            if response.status == 200:
                data = await response.json()
            else:
                data = {"success": False}

    if data["success"]:
        item_name = data["data"]
        await rq.set_inspected_item(user_id, item_name)
        inspected_item = item_name
        keyboard = await inspect_menu(user_language)
        text = get_text(user_language, 'inspect_menu.CURRENTLY_INSPECTING_ITEM').format(inspected_item=inspected_item)

        await message.answer(text=text, parse_mode="Markdown", reply_markup=keyboard)
        await state.clear()
    else:
        await message.answer("No items Found")


@inspect_menu_router.callback_query(F.data.startswith("selected_item_"))
async def handle_selected_item(callback: CallbackQuery, state: FSMContext):
    item_name = callback.data.split("_")[-1]

    user_id = callback.from_user.id
    user_data = await rq.get_state(user_id)
    sel_game_data = user_data.get("sel_game_data")

    # Retrieve user_language from the state
    state_data = await state.get_data()
    user_language = state_data.get('user_language', user_data.get('language'))

    if sel_game_data:
        await rq.set_inspected_item(user_id, item_name)
        inspected_item = item_name

        keyboard = await inspect_menu(user_language)
        text = get_text(user_language, 'inspect_menu.CURRENTLY_INSPECTING_ITEM').format(inspected_item=inspected_item)

        await callback.message.edit_text(text=text, parse_mode="Markdown", reply_markup=keyboard)
        await state.clear()
    else:
        await callback.answer(get_text(user_language, 'inspect_menu.NO_GAME_DATA_ERROR'), show_alert=True)


@inspect_menu_router.callback_query(F.data.startswith("inspect_menu"))
async def select_mode(callback: CallbackQuery, state: FSMContext):
    await show_inspect_menu(callback, state)


@inspect_menu_router.callback_query(F.data.startswith("switch_game"))
async def switch_game_handler(callback: CallbackQuery, state: FSMContext):
    # Retrieve user_language from the state
    state_data = await state.get_data()
    user_language = state_data.get('user_language', callback.from_user.language_code)

    keyboard = await game()
    text = get_text(user_language, 'inspect_menu.SWITCH_GAME')
    await callback.message.edit_text(text=text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()


@inspect_menu_router.callback_query(F.data.startswith("sel_game_"))
async def select_game(callback: CallbackQuery, state: FSMContext):
    sel_game = callback.data.split("_")[-1]
    await rq.switch_game(callback.from_user.id, sel_game)

    # Retrieve user_language from the state
    state_data = await state.get_data()
    user_language = state_data.get('user_language', callback.from_user.language_code)

    await callback.answer(get_text(user_language, 'inspect_menu.GAME_SWITCHED').format(game_name=sel_game),
                          show_alert=False)
    await rq.reset_inspected_item(callback.from_user.id)
    await show_inspect_menu(callback, state)


@inspect_menu_router.callback_query(F.data.startswith("reset_inspected_item"))
async def reset_inspected_item(callback: CallbackQuery, state: FSMContext):
    await rq.reset_inspected_item(callback.from_user.id)

    # Retrieve user_language from the state
    state_data = await state.get_data()
    user_language = state_data.get('user_language', callback.from_user.language_code)

    await callback.answer(get_text(user_language, 'inspect_menu.RESET_INSPECTED_ITEM'), show_alert=False)
    await show_inspect_menu(callback, state)


@inspect_menu_router.callback_query(F.data.startswith("sel_from_favorites"))
async def select_from_favorites(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_data = await rq.get_state(user_id)
    sel_game_data = user_data.get("sel_game_data")

    # Retrieve user_language from the state
    state_data = await state.get_data()
    user_language = state_data.get('user_language', user_data.get('language'))

    result = await rq.get_favorite(user_id, sel_game_data.get("steam_id"))

    if result["success"]:
        data = result["data"]
        keyboard = await favorite_items_list(data, user_language)
        await callback.message.edit_text(
            text=get_text(user_language, 'inspect_menu.FAVORITES_SELECTION'),
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        await callback.answer()

    else:
        keyboard = await back("inspect_menu", user_language)
        await callback.message.edit_text(
            text=get_text(user_language, 'inspect_menu.EMPTY_FAVORITES_LIST'), parse_mode="Markdown",
            reply_markup=keyboard
        )
        await callback.answer()

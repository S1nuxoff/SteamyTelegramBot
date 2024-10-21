from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from typing import Union

from app.utils.errors import get_error_message
from app.api.steam import item_exists
from app.keyboards import (
    inspect_menu,
    setup_inspect_mode,
    game,
    back,
    favorite_items_list,
)
from app.states import SetupItemToInspect

import app.database.requests as rq

inspect_menu_router = Router()


async def item_setup(
    target: Union[CallbackQuery, Message], sel_game_data, state: FSMContext
):
    """
    Prompts the user to select or enter an item to inspect, including the selected game.
    """
    keyboard = await setup_inspect_mode()
    game_name = sel_game_data.get(
        "name", "Unknown Game"
    )  # Получаем название игры из sel_game_data

    text = (
        f"🔗 *Inspect Item menu!*\n"
        "Let’s get started by selecting an item to inspect\n\n"
        "*How would you like to choose your item?*\n"
        "🔍 *Search:* Enter the item name or paste its link\n"
        "🌟 *Favorites:* Select from your saved favorite items\n\n"
        f"🎮 *Selected Game:* _{game_name}_\n\n"
    )

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(
            text=text, parse_mode="Markdown", reply_markup=keyboard
        )
        await target.answer()  # Acknowledge the callback
    elif isinstance(target, Message):
        await target.answer(text=text, parse_mode="Markdown", reply_markup=keyboard)
    # Set the state after sending the message
    await state.set_state(SetupItemToInspect.item_name)


async def show_inspect_menu(target: Union[CallbackQuery, Message], state: FSMContext):
    """
    Displays the main menu if an inspected item exists.
    Otherwise, initiates the item setup process.
    """
    user_id = target.from_user.id
    user_data = await rq.get_state(user_id)
    sel_game_data = user_data.get("sel_game_data")
    inspected_item = user_data.get("inspected_item")

    if inspected_item is None:
        # No inspected item; initiate setup
        await item_setup(target, sel_game_data, state)
    else:
        # Inspected item exists; display main menu
        keyboard = await inspect_menu()
        text = (
            f"🔍 *You are currently inspecting:* *{inspected_item}*\n"
            "This item is now ready for a detailed review.\n\n"
            "*Feel free to dive into the specifics\n*"
            "just use the options in the menu below 👇\n\n"
        )

        if isinstance(target, CallbackQuery):
            await target.message.edit_text(
                text=text, parse_mode="Markdown", reply_markup=keyboard
            )
            await target.answer()  # Acknowledge the callback
        elif isinstance(target, Message):
            await target.answer(text=text, parse_mode="Markdown", reply_markup=keyboard)


@inspect_menu_router.message(SetupItemToInspect.item_name)
async def handle_item_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await rq.get_state(user_id)
    sel_game_data = user_data.get("sel_game_data")
    item_name = message.text.strip()

    result = await item_exists(sel_game_data.get("steam_id"), item_name)
    if result["success"]:
        item_name = result["data"]
        await rq.set_inspected_item(user_id, item_name)
        inspected_item = item_name
        sel_game = sel_game_data.get("steam_id")

        keyboard = await inspect_menu()
        text = (
            f"🎉 *Great choice! You are now inspecting:* *{inspected_item}*\n"
            "This item is now ready for a detailed review.\n\n"
            "*Feel free to dive into the specifics\n*"
            "just use the options in the menu below 👇\n\n"
        )

        # Edit the original setup message to display the main menu
        await message.answer(text=text, parse_mode="Markdown", reply_markup=keyboard)
        await state.clear()  # Clear the state since setup is complete
    else:
        error_message = get_error_message(
            result["error"], details=result.get("details", "")
        )
        await message.answer(error_message)


@inspect_menu_router.callback_query(F.data.startswith("selected_item_"))
async def handle_selected_item(callback: CallbackQuery, state: FSMContext):
    item_name = callback.data.split("_")[-1]

    user_id = callback.from_user.id
    user_data = await rq.get_state(user_id)
    sel_game_data = user_data.get("sel_game_data")

    if sel_game_data:
        await rq.set_inspected_item(user_id, item_name)
        inspected_item = item_name
        sel_game = sel_game_data.get("steam_id")
        keyboard = await inspect_menu()
        text = (
            f"🔍 *You are currently inspecting:* *{inspected_item}*\n"
            "This item is now ready for a detailed review.\n\n"
            "*Feel free to dive into the specifics\n*"
            "just use the options in the menu below 👇\n\n"
        )
        await callback.message.edit_text(
            text=text, parse_mode="Markdown", reply_markup=keyboard
        )
        await state.clear()
    else:
        await callback.answer("❌ *Error:* Game data not found.", show_alert=True)


@inspect_menu_router.callback_query(F.data.startswith("inspect_menu"))
async def select_mode(callback: CallbackQuery, state: FSMContext):
    await show_inspect_menu(callback, state)


@inspect_menu_router.callback_query(F.data.startswith("switch_game"))
async def switch_game_handler(callback: CallbackQuery, state: FSMContext):
    keyboard = await game()
    text = (
        "🎮 *Switch Game*\n\n"
        "*Want to explore something new?*\n"
        "Just select the game you'd like to switch to."
    )
    await callback.message.edit_text(
        text=text, parse_mode="Markdown", reply_markup=keyboard
    )
    await callback.answer()


@inspect_menu_router.callback_query(F.data.startswith("sel_game_"))
async def select_game(callback: CallbackQuery, state: FSMContext):
    sel_game = callback.data.split("_")[-1]
    await rq.switch_game(callback.from_user.id, sel_game)
    await callback.answer(f"✅ *Game switched to:* {sel_game}", show_alert=False)
    await rq.reset_inspected_item(callback.from_user.id)
    await show_inspect_menu(callback, state)


@inspect_menu_router.callback_query(F.data.startswith("reset_inspected_item"))
async def reset_inspected_item(callback: CallbackQuery, state: FSMContext):
    await rq.reset_inspected_item(callback.from_user.id)
    await callback.answer("✅ *Item changed successfully!*", show_alert=False)
    await show_inspect_menu(callback, state)


@inspect_menu_router.callback_query(F.data.startswith("add_to_favorite"))
async def add_to_favorite(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_data = await rq.get_state(user_id)
    sel_game_data = user_data.get("sel_game_data")
    item = user_data.get("inspected_item")

    result = await rq.add_favorite(user_id, sel_game_data.get("steam_id"), item)
    if result["success"]:
        await callback.answer("🌟 *Item added to your favorites!*", show_alert=False)
    else:
        error_message = get_error_message(
            result["error"], details=result.get("details", "")
        )
        await callback.answer(error_message, show_alert=True)


@inspect_menu_router.callback_query(F.data.startswith("sel_from_favorites"))
async def select_from_favorites(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_data = await rq.get_state(user_id)
    sel_game_data = user_data.get("sel_game_data")

    result = await rq.get_favorite(user_id, sel_game_data.get("steam_id"))

    if result["success"]:
        data = result["data"]
        keyboard = await favorite_items_list(data)
        await callback.message.edit_text(
            text="🌟 *Select an item from your favorites:*",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        await callback.answer()

    else:
        keyboard = await back("inspect_menu")
        error_message = get_error_message(
            result["error"], details=result.get("details", "")
        )
        await callback.message.edit_text(
            text=error_message, parse_mode="Markdown", reply_markup=keyboard
        )
        await callback.answer()

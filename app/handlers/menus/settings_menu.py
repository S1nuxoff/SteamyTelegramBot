from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards import settings_menu, settings_currency, settings_language
from app.utils.localization import get_text

import app.database.requests as rq

settings_menu_router = Router()

# Function to show the settings menu, retrieving and using the user's language
async def show_settings_menu(callback: CallbackQuery, state: FSMContext):
    # Retrieve the user's language from the database
    user_data = await rq.get_state(callback.from_user.id)
    user_language = user_data.get('language')

    # Store the user's language in FSM context
    await state.update_data(user_language=user_language)

    keyboard = await settings_menu(user_language)

    # Use the localized text for the settings menu
    text = get_text(user_language, 'settings_menu.SETTINGS_MENU_TEXT')

    await callback.message.edit_text(
        text=text, parse_mode="Markdown", reply_markup=keyboard
    )


@settings_menu_router.callback_query(F.data == "settings_menu")
async def handle_settings(callback: CallbackQuery, state: FSMContext):
    await show_settings_menu(callback, state)


@settings_menu_router.callback_query(F.data == "settings_currency")
async def handle_settings_currency(callback: CallbackQuery, state: FSMContext):
    # Retrieve the user's language from FSM context
    data = await state.get_data()
    user_language = data.get('user_language')

    keyboard = await settings_currency()

    # Use the localized text for the currency selection menu
    text = get_text(user_language, 'settings_menu.SELECT_CURRENCY_TEXT')

    await callback.message.edit_text(
        text=text, parse_mode="Markdown", reply_markup=keyboard
    )

# Handler for currency selection
@settings_menu_router.callback_query(F.data.startswith("currency_"))
async def handle_currency_selection(callback: CallbackQuery, state: FSMContext):

    user_id = callback.from_user.id
    data = callback.data  # Expected format "currency_{id}"

    _, currency_id_str = data.split("_", 1)
    currency_id = int(currency_id_str)

    # Update the currency in the database
    await rq.set_currency(user_id, currency_id)

    # Retrieve the user's language from FSM context
    state_data = await state.get_data()
    user_language = state_data.get('user_language')

    # Use the localized confirmation message
    text = get_text(user_language, 'settings_menu.CURRENCY_UPDATE_CONFIRMATION')

    await callback.answer(
        text=text,
        parse_mode="Markdown",
    )
    await show_settings_menu(callback, state)

@settings_menu_router.callback_query(F.data == "settings_language")
async def handle_settings_currency(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    user_language = data.get('user_language')

    keyboard = await settings_language()

    text = get_text(user_language, 'settings_menu.SELECT_LANGUAGE_TEXT')

    await callback.message.edit_text(
        text=text, parse_mode="Markdown", reply_markup=keyboard
    )

@settings_menu_router.callback_query(F.data.startswith("language_"))
async def handle_currency_selection(callback: CallbackQuery, state: FSMContext):

    user_id = callback.from_user.id
    data = callback.data  # Expected format "currency_{id}"

    _, language_code = data.split("_", 1)
    language_code = int(language_code)

    # Update the currency in the database
    await rq.set_language(user_id, language_code)

    state_data = await state.get_data()
    user_language = state_data.get('user_language')

    # Use the localized confirmation message
    text = get_text(user_language, 'settings_menu.CURRENCY_UPDATE_CONFIRMATION')

    await callback.answer(
        text=text,
        parse_mode="Markdown",
    )
    await show_settings_menu(callback, state)
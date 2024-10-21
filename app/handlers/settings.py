from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards import settings_menu, settings_currency

import app.database.requests as rq

settings_menu_router = Router()


async def show_settings_menu(callback):
    keyboard = await settings_menu()
    text = (
        "⚙️ *Settings Menu*\n\n"
        "Here you can adjust all your preferences.\n"
        "Take your time and explore the options!"
    )

    await callback.message.edit_text(
        text=text, parse_mode="Markdown", reply_markup=keyboard
    )


@settings_menu_router.callback_query(F.data == "settings_menu")
async def handle_settings(callback: CallbackQuery):
    await show_settings_menu(callback)


@settings_menu_router.callback_query(F.data == "settings_currency")
async def handle_settings_currency(callback: CallbackQuery):
    keyboard = await settings_currency()
    text = (
        "💰 *Choose Your Currency*\n\n"
        "Select the currency you prefer to see in the app.\n"
        "Once selected, it will be applied to all price displays."
    )

    await callback.message.edit_text(
        text=text, parse_mode="Markdown", reply_markup=keyboard
    )


# Новый хендлер для обработки выбранной валюты
@settings_menu_router.callback_query(F.data.startswith("currency_"))
async def handle_currency_selection(callback: CallbackQuery):

    user_id = callback.from_user.id
    data = callback.data  # Ожидается формат "currency_{id}"

    _, currency_id_str = data.split("_", 1)
    currency_id = int(currency_id_str)

    await rq.set_currency(user_id, currency_id)

    confirmation_text = f"✅ Your currency has been updated!"
    await callback.answer(
        text=confirmation_text,
        parse_mode="Markdown",
    )
    await show_settings_menu(callback)

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.requests import get_currencies


async def settings_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🌍 Language", callback_data="settings_language"
                ),
                InlineKeyboardButton(
                    text="💰 Currency", callback_data="settings_currency"
                ),
            ],
            [InlineKeyboardButton(text="« Back", callback_data="main_menu")],
        ]
    )


async def settings_currency():
    currencies = await get_currencies()
    builder = InlineKeyboardBuilder()

    for currency in currencies:
        builder.add(
            InlineKeyboardButton(
                text=currency["name"], callback_data=f"currency_{currency['id']}"
            )
        )

    builder.row(InlineKeyboardButton(text="« Back", callback_data="settings_menu"))

    return builder.as_markup()

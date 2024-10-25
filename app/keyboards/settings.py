from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.requests import get_currencies, get_languages
from app.utils.localization import get_text

async def settings_menu(user_language):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text(user_language, 'buttons.LANGUAGE_BUTTON'), callback_data="settings_language"
                ),
                InlineKeyboardButton(
                    text=get_text(user_language, 'buttons.CURRENCY_BUTTON'), callback_data="settings_currency"
                ),
            ],
            [InlineKeyboardButton(text=get_text(user_language, 'buttons.BACK_BUTTON'), callback_data="main_menu")],
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


async def settings_language():
    languages = await get_languages()
    keyboard_builder = InlineKeyboardBuilder()

    for language in languages:
        keyboard_builder.button(
            text=language["name"], callback_data=f"language_{language['id']}"
        )

    keyboard_builder.adjust(2)

    return keyboard_builder.as_markup()

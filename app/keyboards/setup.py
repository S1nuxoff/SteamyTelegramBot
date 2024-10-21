from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.requests import get_games


async def language():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇦 Українська", callback_data="sel_lang_uk"),
                InlineKeyboardButton(text="🇵🇱 Polska", callback_data="sel_lang_pl"),
            ],
            [InlineKeyboardButton(text="🇺🇸 English", callback_data="sel_lang_en")],
        ]
    )


async def currency():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇦 UAH", callback_data="sel_currency_UAH"),
                InlineKeyboardButton(text="🇵🇱 PLN", callback_data="sel_currency__PLN"),
            ],
            [InlineKeyboardButton(text="🇺🇸 USD", callback_data="sel_currency__USD")],
        ]
    )


async def game():
    games = await get_games()

    # Create the builder object
    keyboard_builder = InlineKeyboardBuilder()

    # Add buttons for each game (2 per row)
    for game in games:
        keyboard_builder.button(
            text=game["name"], callback_data=f"sel_game_{game['name']}"
        )

    # Adjust the button arrangement: 2 buttons per row
    keyboard_builder.adjust(2)

    # Build the keyboard and return
    return keyboard_builder.as_markup()


async def setup_done():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Let's Go", callback_data="main_menu"),
            ],
        ]
    )

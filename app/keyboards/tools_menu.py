from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def tool_setup() -> InlineKeyboardMarkup:

    keyboard = [
        [
            InlineKeyboardButton(
                text="🌟 Select from Favorites", callback_data="sel_from_favorites"
            ),
            InlineKeyboardButton(text="< Back", callback_data="inspect_menu"),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

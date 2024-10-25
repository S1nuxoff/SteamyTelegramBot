from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.localization import get_text

async def main_menu(user_language) -> InlineKeyboardMarkup:

    keyboard = [
        [
            InlineKeyboardButton(text=get_text(user_language, 'buttons.INSPECT_ITEM_BUTTON'), callback_data="inspect_menu"),
            InlineKeyboardButton(text=get_text(user_language, 'buttons.FLOAT_CHECKER_BUTTON'), callback_data="check_float"),
        ],
        [
            InlineKeyboardButton(
                text=get_text(user_language, 'buttons.INVENTORY_VALUE_BUTTON'), callback_data="inventory_value"
            ),
            InlineKeyboardButton(text=get_text(user_language, 'buttons.GET_PREMIUM_BUTTON'), callback_data="get_premium"),
        ],
        [
            InlineKeyboardButton(text=get_text(user_language, 'buttons.SUPPORT_BUTTON'), url="https://t.me/sinuxoff"),
            InlineKeyboardButton(text=get_text(user_language, 'buttons.SETTINGS_BUTTON'), callback_data="settings_menu"),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

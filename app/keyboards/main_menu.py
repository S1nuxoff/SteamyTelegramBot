from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def main_menu() -> InlineKeyboardMarkup:

    keyboard = [
        [
            InlineKeyboardButton(text="Inspect Item", callback_data="inspect_menu"),
            InlineKeyboardButton(text="Float Checker", callback_data="check_float"),
        ],
        [
            InlineKeyboardButton(
                text="Inventory Value", callback_data="inventory_value"
            ),
            InlineKeyboardButton(text="⭐️ Get Premium", callback_data="get_premium"),
        ],
        [
            InlineKeyboardButton(text="Support", url="https://t.me/sinuxoff"),
            InlineKeyboardButton(text="⚙️ Settings", callback_data="settings_menu"),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

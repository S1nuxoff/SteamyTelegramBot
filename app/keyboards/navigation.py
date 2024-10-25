from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.localization import get_text

def start():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Get started", callback_data="get_started")]
        ]
    )


async def back(callback, user_language):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=get_text(user_language, 'buttons.BACK_BUTTON'), callback_data=callback)]]
    )

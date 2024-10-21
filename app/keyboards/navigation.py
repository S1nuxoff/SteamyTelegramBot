from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Get started", callback_data="get_started")]
        ]
    )


async def back(callback):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="« Back", callback_data=callback)]]
    )

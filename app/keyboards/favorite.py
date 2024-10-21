from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def back_next():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="« Back", callback_data="nav_back"),
            ]
        ]
    )


# async def empty_favotite():
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [
#             InlineKeyboardButton(text='« Back', callback_data="nav_back"),
#         ]
#     ])

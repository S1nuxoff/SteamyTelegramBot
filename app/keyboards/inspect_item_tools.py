from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.localization import localization, get_text


async def inspect_menu(user_language) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text=get_text(user_language, 'buttons.COMPARE_PRICES_BUTTON'),
                                 callback_data="compare_prices"),

            InlineKeyboardButton(text=get_text(user_language, 'buttons.PRICE_CHART_BUTTON'),
                                 callback_data="price_chart"),
        ]
    ]

    keyboard.extend(
        [
            [
                InlineKeyboardButton(text=get_text(user_language, 'buttons.PRICE_ALERT_BUTTON'),
                                     callback_data="price_alert"),
                InlineKeyboardButton(
                    text=get_text(user_language, 'buttons.CHECK_LIQUIDITY_BUTTON'), callback_data="check_liquidity"
                ),
            ],
            [
                # Check the favorite value and create the corresponding button
                InlineKeyboardButton(
                    text=get_text(user_language, 'buttons.ADD_TO_FAVORITE_BUTTON'), callback_data="add_to_favorite"
                ),
                InlineKeyboardButton(
                    text=get_text(user_language, 'buttons.CHANGE_ITEM_BUTTON'), callback_data="reset_inspected_item"
                ),
            ],
            [
                InlineKeyboardButton(text=get_text(user_language, 'buttons.BACK_BUTTON'), callback_data="main_menu"),
            ],
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def setup_inspect_mode(user_language) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text=get_text(user_language, 'buttons.FAVORITES_BUTTON'), callback_data="sel_from_favorites"
            ),
            InlineKeyboardButton(text=get_text(user_language, 'buttons.SWITCH_GAME_BUTTON'),
                                 callback_data="switch_game"),
        ],
        [
            InlineKeyboardButton(text=get_text(user_language, 'buttons.BACK_BUTTON'), callback_data="main_menu"),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# async def confirm_delete_favorite() -> InlineKeyboardMarkup:
#     keyboard = [
#         [
#             InlineKeyboardButton(
#                 text="✅ Yes, delete", callback_data=f"confirm_delete"
#             ),
#             InlineKeyboardButton(text="❌ Cancel", callback_data="inspect_menu"),
#         ]
#     ]
#
#     return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def favorite_items_list(items, user_language):
    keyboard = InlineKeyboardBuilder()
    for item in items:
        keyboard.add(
            InlineKeyboardButton(
                text=f"{item['hash_name']}",
                callback_data=f"selected_item_{item['hash_name']}",
            )
        )
    keyboard.add(
        InlineKeyboardButton(text=get_text(user_language, 'buttons.BACK_BUTTON'), callback_data="inspect_menu"))
    keyboard.adjust(2)
    return keyboard.as_markup()


async def chart_period(user_language):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_text(user_language, 'buttons.PERIOD_DAY_BUTTON'), callback_data="chart_period_day"
                ),
                InlineKeyboardButton(
                    text=get_text(user_language, 'buttons.PERIOD_WEEK_BUTTON'), callback_data="chart_period_week"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=get_text(user_language, 'buttons.PERIOD_MONTH_BUTTON'), callback_data="chart_period_month"
                ),
                InlineKeyboardButton(
                    text=get_text(user_language, 'buttons.PERIOD_ALL_BUTTON'), callback_data="chart_period_lifetime"
                ),
            ],
            [InlineKeyboardButton(text="« Back", callback_data="inspect_menu")],
        ]
    )
    return keyboard

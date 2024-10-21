from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def inspect_menu() -> InlineKeyboardMarkup:

    keyboard = [
        [
            InlineKeyboardButton(text="Compare Prices", callback_data="compare_prices"),
            InlineKeyboardButton(text="Price Chart", callback_data="price_chart"),
        ]
    ]

    keyboard.extend(
        [
            [
                InlineKeyboardButton(text="Price Alert", callback_data="price_alert"),
                InlineKeyboardButton(
                    text="Check Liquidity", callback_data="check_liquidity"
                ),
            ],
            [
                # Проверяем значение favorite и создаем соответствующую кнопку
                InlineKeyboardButton(
                    text="Add to Favorite🌟", callback_data="add_to_favorite"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Change Item", callback_data="reset_inspected_item"
                ),
                InlineKeyboardButton(text="« Back to Main", callback_data="main_menu"),
            ],
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def setup_inspect_mode() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="🌟 Favorites", callback_data="sel_from_favorites"
            ),
            InlineKeyboardButton(text="🔄 Switch Game", callback_data="switch_game"),
        ],
        [
            InlineKeyboardButton(text="«  Back", callback_data="main_menu"),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def confirm_delete_favorite() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="✅ Yes, delete", callback_data=f"confirm_delete"
            ),
            InlineKeyboardButton(text="❌ Cancel", callback_data="inspect_menu"),
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def favorite_items_list(items):
    keyboard = InlineKeyboardBuilder()
    for item in items:
        keyboard.add(
            InlineKeyboardButton(
                text=f"{item['hash_name']}",
                callback_data=f"selected_item_{item['hash_name']}",
            )
        )

    keyboard.adjust(2)
    keyboard.add(InlineKeyboardButton(text="« Back", callback_data="inspect_menu"))
    return keyboard.as_markup()


async def chart_period():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Last 24 Hours", callback_data="chart_period_day"
                ),
                InlineKeyboardButton(
                    text="Last Week", callback_data="chart_period_week"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Last Moth", callback_data="chart_period_month"
                ),
                InlineKeyboardButton(
                    text="Lifetime", callback_data="chart_period_lifetime"
                ),
            ],
            [InlineKeyboardButton(text="« Back", callback_data="inspect_menu")],
        ]
    )
    return keyboard

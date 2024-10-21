from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from app.keyboards import back


import app.database.requests as rq

favorite_router = Router()


@favorite_router.callback_query(F.data.startswith("sel_from_favorites"))
async def select_mode(callback: CallbackQuery):
    favorite_list = await rq.get_favorite(callback.from_user.id)
    if favorite_list:
        pass
    else:
        keyboard = await back()
        await callback.message.edit_text(
            text=(
                "🧐 *Looks like your favorites list is empty\n*"
                "You can easily add items later!"
            ),
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        await callback.answer()

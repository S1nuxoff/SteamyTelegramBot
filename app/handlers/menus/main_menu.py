from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards import main_menu

from app.utils.localization import get_text
import app.database.requests as rq

main_menu_router = Router()

# TODO: Sticker, Pistol, SMG, Rifle, Sniper Rifle, Shotgun, Graffiti, Container, Machinegun

async def show_main_menu(callback: CallbackQuery, state: FSMContext):
    user_data = await rq.get_state(callback.from_user.id)
    await state.clear()
    user_language = user_data.get('language')

    text = get_text(user_language, 'main_menu.WELCOME_TEXT')
    keyboard = await main_menu(user_language)

    await callback.message.edit_text(
        text=text, parse_mode="Markdown", reply_markup=keyboard
    )
    await callback.answer()

@main_menu_router.callback_query(F.data.startswith("main_menu"))
async def handle_main_menu(callback: CallbackQuery, state: FSMContext):
    await show_main_menu(callback, state)


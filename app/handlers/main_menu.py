from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.utils.errors import get_error_message
from app.keyboards import main_menu, back, language
from app.states import SetupItemToFloatCheck
from app.utils.get_float import get_float_data

from app.localization import localization, get_text
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
async def select_main_menu(callback: CallbackQuery, state: FSMContext):
    await show_main_menu(callback, state)

@main_menu_router.callback_query(F.data.startswith("check_float"))
async def handle_check_float(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SetupItemToFloatCheck.rungame_url)
    user_data = await rq.get_state(callback.from_user.id)
    user_language = user_data.get('language')

    text = get_text(user_language, 'check_float.CHECK_FLOAT_TEXT')
    keyboard = await back("main_menu", user_language)

    await callback.message.edit_text(
        text=text, parse_mode="Markdown", reply_markup=keyboard
    )
    await callback.answer()


@main_menu_router.message(SetupItemToFloatCheck.rungame_url)
async def process_rungame_link(message: Message, state: FSMContext):
    user_input = message.text
    user_data = await rq.get_state(message.from_user.id)  # Corrected `callback` to `message`
    user_language = user_data.get('language')

    if "rungame" in user_input:
        data = await get_float_data(user_input)
        if data:

            text = get_text(
                user_language,
                'check_float.ITEM_DETAILS'
            ).format(
                paint_seed=data['paint_seed'],
                paint_index=data['paint_index'],
                float_value=data['float_value']
            )

            await message.answer(
                text=text, parse_mode="Markdown", reply_markup=await back("main_menu", user_language)
            )

            await state.clear()
        else:
            text = get_text(user_language, 'errors.DATA_ERROR')
            await message.answer(
                text=text,
                reply_markup=await back("main_menu", user_language),
                parse_mode="Markdown",
            )
    else:
        text = get_text(user_language, 'check_float.INVALID_RUNGAME_LINK')
        await message.answer(
            text=text,
            reply_markup=await back("main_menu", user_language),
            parse_mode="Markdown",
        )

@main_menu_router.callback_query(F.data.startswith("back"))
async def go_back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await show_main_menu(callback, state)


# Handling other buttons with a placeholder
@main_menu_router.callback_query(F.data.startswith("inventory_value"))
async def handle_inventory_value(callback: CallbackQuery):
    user_data = await rq.get_state(callback.from_user.id)
    user_language = user_data.get('language')

    text = get_text(user_language, 'other.COMING_SOON')
    await callback.answer(
        text=text,
        show_alert=True,
    )

@main_menu_router.callback_query(F.data.startswith("get_premium"))
async def handle_get_premium(callback: CallbackQuery):
    user_data = await rq.get_state(callback.from_user.id)
    user_language = user_data.get('language')

    text = get_text(user_language, 'other.COMING_SOON')
    await callback.answer(
        text=text,
        show_alert=True,
    )

@main_menu_router.callback_query(F.data.startswith("price_alert"))
async def handle_price_alert(callback: CallbackQuery):
    user_data = await rq.get_state(callback.from_user.id)
    user_language = user_data.get('language')

    text = get_text(user_language, 'other.COMING_SOON')
    await callback.answer(
        text=text,
        show_alert=True,
    )

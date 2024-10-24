from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.keyboards import main_menu, back
from app.states import SetupItemToFloatCheck
from app.tools.get_float import get_float_data

from app.localization import get_text
import app.database.requests as rq

main_tools_router = Router()


@main_tools_router.callback_query(F.data.startswith("check_float"))
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


@main_tools_router.message(SetupItemToFloatCheck.rungame_url)
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

# Handling other buttons with a placeholder
@main_tools_router.callback_query(F.data.startswith("inventory_value"))
async def handle_inventory_value(callback: CallbackQuery):
    user_data = await rq.get_state(callback.from_user.id)
    user_language = user_data.get('language')

    text = get_text(user_language, 'other.COMING_SOON')
    await callback.answer(
        text=text,
        show_alert=True,
    )

@main_tools_router.callback_query(F.data.startswith("get_premium"))
async def handle_get_premium(callback: CallbackQuery):
    user_data = await rq.get_state(callback.from_user.id)
    user_language = user_data.get('language')

    text = get_text(user_language, 'other.COMING_SOON')
    await callback.answer(
        text=text,
        show_alert=True,
    )

@main_tools_router.callback_query(F.data.startswith("price_alert"))
async def handle_price_alert(callback: CallbackQuery):
    user_data = await rq.get_state(callback.from_user.id)
    user_language = user_data.get('language')

    text = get_text(user_language, 'other.COMING_SOON')
    await callback.answer(
        text=text,
        show_alert=True,
    )

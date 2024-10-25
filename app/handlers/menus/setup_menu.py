# app/handlers/setup_menu.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
import app.database.requests as rq
from app.keyboards import language, currency, game, setup_done
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from app.states.states import SetupStates
from app.handlers.menus.main_menu import show_main_menu
from app.utils.localization import get_text

setup_router = Router()


@setup_router.callback_query(F.data == "get_started")
async def setup_start(callback_query: CallbackQuery, state: FSMContext):
    data = await rq.get_state(callback_query.from_user.id)
    setup_status = data.get("setup_status")

    if not setup_status:
        await state.set_state(SetupStates.language)
        keyboard_setup = await language()


        text = get_text('en', 'setup.SETUP_LANGUAGE_TEXT')

        await callback_query.message.answer(
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard_setup,
        )
    else:
        await show_main_menu(callback_query, state)

    await callback_query.answer()


@setup_router.callback_query(
    StateFilter(SetupStates.language), F.data.startswith("sel_lang_")
)
async def select_language(callback: CallbackQuery, state: FSMContext):
    sel_lang = callback.data.split("_")[-1]
    await state.update_data(language=sel_lang)
    await state.set_state(SetupStates.currency)
    keyboard = await currency()
    # Получаем локализованный текст для шага 2
    text = get_text(sel_lang, 'setup.SETUP_CURRENCY_TEXT')

    await callback.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
    await callback.answer()


@setup_router.callback_query(
    StateFilter(SetupStates.currency), F.data.startswith("sel_currency_")
)
async def select_currency(callback: CallbackQuery, state: FSMContext):
    sel_currency = callback.data.split("_")[-1]
    await state.update_data(currency=sel_currency)
    await state.set_state(SetupStates.game)  # Переходим к следующему шагу - выбор игры
    keyboard = await game()
    data = await state.get_data()
    # Получаем локализованный текст для шага 4 (предполагая, что шаг 3 уже реализован)
    text = get_text(data.get('language'), 'setup.SETUP_LANGUAGE_TEXT')

    await callback.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
    await callback.answer()


@setup_router.callback_query(
    StateFilter(SetupStates.game), F.data.startswith("sel_game_")
)
async def select_game(callback: CallbackQuery, state: FSMContext):
    sel_game = callback.data.split("_")[-1]
    await state.update_data(game=sel_game)
    data = await state.get_data()

    language = data.get("language")
    currency = data.get("currency")
    game_selected = data.get("game")

    await rq.set_setup(callback.from_user.id, language, currency, game_selected)

    keyboard = await setup_done()

    # Получаем локализованный текст для завершения настройки
    text = get_text(language, 'setup.SETUP_COMPLETION_TEXT')

    await callback.message.edit_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
    await state.clear()
    await callback.answer()

from aiogram import Router, F
from aiogram.types import CallbackQuery
import app.database.requests as rq
from app.keyboards import language, currency, game, setup_done
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from app.states import SetupStates
from app.handlers.main_menu import show_main_menu

setup_router = Router()


@setup_router.callback_query(F.data == "get_started")
async def setup_start(callback_query: CallbackQuery, state: FSMContext):

    data = await rq.get_state(callback_query.from_user.id)
    setup_status = data.get("setup_status")

    if not setup_status:
        await state.set_state(SetupStates.language)
        keyboard_setup = await language()
        await callback_query.message.answer(
            text=(
                "⚙️ *Let's quickly set up your preferences!*\n"
                "This setup will take no more than 10 seconds.\n\n"
                "*📌 Step 1️ / 4*\n"
                "*Please select your preferred language.*\n"
                "This choice will determine how you interact with the bot\n\n"
                "☺️   *Don't worry, you can change it later in the settings*"
            ),
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
    await callback.message.edit_text(
        text=(
            "⚙️ *Set up your preferences*\n\n"
            "📌 *Step 2️ / 4*\n"
            "*Please select your preferred currency.\n*"
            "This choice will determine how item values are shown in the bot\n\n"
            "☺️   *Don't worry, you can change it later in the settings*"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
    await callback.answer()


@setup_router.callback_query(
    StateFilter(SetupStates.currency), F.data.startswith("sel_currency_")
)
async def select_mode(callback: CallbackQuery, state: FSMContext):
    sel_currency = callback.data.split("_")[-1]
    await state.update_data(currency=sel_currency)
    await state.set_state(SetupStates.game)  # Переходим к следующему шагу - выбор игры
    keyboard = await game()
    await callback.message.edit_text(
        text=(
            "⚙️ *Set up your preferences*\n\n"
            "📌 *Step 4 / 4*\n"
            "*Please select your preferred game.\n\n*"
            "☺️   *Don't worry, you can change it later in the settings*"
        ),
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
    await callback.message.edit_text(
        text=(
            "🤩 *Fantastic news!*\n\n"
            "*Your bot is ready and waiting for you.*\n"
            "Jump in and explore all the exciting features it has to offer!\n\n"
            "🚀  *To start using the bot, press the button below now!!*"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard,
    )
    await state.clear()
    await callback.answer()

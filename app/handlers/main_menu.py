from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.utils.errors import get_error_message
from app.keyboards import main_menu, back
from app.states import SetupItemToFloatCheck
from app.utils.get_float import get_float_data

import app.database.requests as rq

main_menu_router = Router()

# TODO: Sticker, Pistol, SMG, Rifle, Sniper Rifle, Shotgun, Graffiti, Container, Machinegun


async def show_main_menu(callback: CallbackQuery, state: FSMContext):
    # Clear the state when returning to the main menu
    await state.clear()

    keyboard = await main_menu()
    text = (
        "🔥 *Welcome to Steamy!*\n"
        "Great to see you here! Let's get started.\n\n"
        "👇 Pick an option below, and we’ll dive right in!\n"
        "*I'm always here if you need anything.*"
    )

    await callback.message.edit_text(
        text=text, parse_mode="Markdown", reply_markup=keyboard
    )
    await callback.answer()


@main_menu_router.callback_query(F.data.startswith("main_menu"))
async def select_main_menu(callback: CallbackQuery, state: FSMContext):
    await show_main_menu(callback, state)


@main_menu_router.callback_query(F.data.startswith("check_float"))
async def handle_check_float(callback: CallbackQuery, state: FSMContext):
    # Set the state to wait for the user's link
    await state.set_state(SetupItemToFloatCheck.rungame_url)

    text = (
        f"🔍 *Float Check*\n\n"
        f"To help you find the float value of your item, please send us the 'rungame' link from Steam.\n\n"
        f"*Here's how you can get it:*\n"
        f"1. Right-click on the item in your inventory.\n"
        f"2. Select *Inspect in Game*.\n"
        f"3. Copy the link from your browser's address bar.\n"
        f"4. Paste it here and send it to us.\n\n"
        f"If you need any assistance, don't hesitate to ask!"
    )

    keyboard = await back("main_menu")

    await callback.message.edit_text(
        text=text, parse_mode="Markdown", reply_markup=keyboard
    )
    await callback.answer()


@main_menu_router.message(SetupItemToFloatCheck.rungame_url)
async def process_rungame_link(message: Message, state: FSMContext):
    user_input = message.text
    # Check if the entered text is a link
    if "rungame" in user_input:
        data = await get_float_data(user_input)

        if data:
            # Format the response
            text = (
                f"🎉 *Here are the details of your item:*\n\n"
                f"• **Paint Seed:** {data['paint_seed']}\n"
                f"• **Paint Index:** {data['paint_index']}\n"
                f"• **Float Value:** {data['float_value']:.6f}\n\n"
                "Thank you for using our service! If there's anything else we can assist you with, please let us know."
            )

            await message.answer(
                text=text, parse_mode="Markdown", reply_markup=await back("main_menu")
            )

            await state.clear()
        else:
            await message.answer(
                "❌ *Oops! We couldn't retrieve your item data at the moment.*\n\n"
                "Please try again later, and if the issue persists, feel free to contact our support team.",
                reply_markup=await back("main_menu"),
                parse_mode="Markdown",
            )
    else:
        await message.answer(
            f"⚠️ *Hmm, that doesn't seem to be a valid 'rungame' link.*\n\n"
            f"Please make sure you're sending the correct link from Steam. If you need help, here's how to get it:\n"
            f"1. Right-click on the item in your inventory.\n\n"
            f"2. Select *Inspect in Game*.\n"
            f"3. Copy the link from your browser and send it here.",
            reply_markup=await back("main_menu"),
            parse_mode="Markdown",
        )


@main_menu_router.callback_query(F.data.startswith("back"))
async def go_back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await show_main_menu(callback, state)


# Handling other buttons with a placeholder
@main_menu_router.callback_query(F.data.startswith("inventory_value"))
async def handle_inventory_value(callback: CallbackQuery):
    await callback.answer(
        "🚧 *Coming Soon!*\n\n"
        "We're working hard to bring this feature to you. Stay tuned for updates!",
        show_alert=True,
    )


@main_menu_router.callback_query(F.data.startswith("get_premium"))
async def handle_get_premium(callback: CallbackQuery):
    await callback.answer(
        "🚧 *Get Premium*\n\n"
        "Exciting features are on the way! We'll let you know as soon as they're available.",
        show_alert=True,
    )


@main_menu_router.callback_query(F.data.startswith("price_alert"))
async def handle_price_alert(callback: CallbackQuery):
    await callback.answer(
        "🚧 *Price Alerts*\n\n"
        "We're working on this feature to help you stay informed. Check back soon!",
        show_alert=True,
    )

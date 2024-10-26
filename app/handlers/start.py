# app/handlers/start.py

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
import app.database.requests as rq
from app.keyboards import start


start_router = Router()

# setup_status = await rq.get_setup_status(message.from_user.id)


@start_router.message(CommandStart())
async def cmd_start(message: Message):

    user_name = message.from_user.first_name

    await rq.set_user(message.from_user.id, user_name)

    await message.answer(
        text=(
            "👋🏻 *Hello, I’m Steamy.*\n Helping you find deals, track prices, and manage your inventory\n\n"
            "😏 *What can I do for you?*\n\n"
            "•  *Price Comparison:* Find the best deals across platforms.\n"
            "•  *Chart Analysis:* Track and analyze price trends.\n"
            "•  *Liquidity Check:* See how easily items can be sold.\n"
            "•  *Price Alerts:* Get price change notifications.\n"
            "•  *Float Info:* Check items quality with Float values.\n"
            "•  *Best Float Search:* Find the best Float offers\n\n"
            "*Ready to explore? Let’s get started!* 🚀"
        ),
        parse_mode="Markdown",
        reply_markup=start(),
    )

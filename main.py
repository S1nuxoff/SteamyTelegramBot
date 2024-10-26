# api.py
import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router
from app.database.models import async_main

import config as cfg


async def start_bot():
    await async_main()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


async def main():

    bot_task = asyncio.create_task(start_bot())
    await asyncio.gather(bot_task)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")

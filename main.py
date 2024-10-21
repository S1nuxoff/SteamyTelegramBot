import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router
from app.database.models import async_main
import uvicorn
from bot_api import app  # импортируем наше FastAPI приложение

# from config import (
#     ITEM_ORDERS_HISTOGRAM_URL,
#     STEAM_BASE_URL,
#     STEAM_PRICE_OVERVIEW_URL,
#     STEAM_MARKET_LISTINGS_URL,
#     DMARKET_MARKET_ITEMS_URL,
# )
import config as cfg


async def start_bot():
    await async_main()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


# async def start_api():
#     config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
#     server = uvicorn.Server(config)
#     await server.serve()


async def main():
    # Создаем задачи для одновременного запуска
    bot_task = asyncio.create_task(start_bot())
    # api_task = asyncio.create_task(start_api())

    # # Ожидаем выполнения обеих задач
    # await asyncio.gather(bot_task, api_task)
    await asyncio.gather(bot_task)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")

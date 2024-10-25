from aiogram import types, BaseMiddleware
from datetime import datetime
from app.database.requests import update_user_activity  # Импортируем функцию обновления активности


class LastActivityMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: types.TelegramObject, data: dict):
        user_id = None

        if isinstance(event, types.Message):
            user_id = event.from_user.id
        elif isinstance(event, types.CallbackQuery):
            user_id = event.from_user.id
        elif hasattr(event, 'from_user') and event.from_user:
            user_id = event.from_user.id

        if user_id:
            current_time = datetime.now()

            await update_user_activity(user_id, current_time)

        # Proceed to the next handler
        return await handler(event, data)
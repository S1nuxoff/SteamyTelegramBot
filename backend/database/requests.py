from backend.database.models import Game, Currency, async_session
from sqlalchemy import select


async def get_game_data(appid):
    async with async_session() as session:
        # Добавляем фильтрацию по steam_id
        result = await session.scalars(select(Game).where(Game.steam_id == appid))
        game = result.one_or_none()  # Используем one_or_none для получения одного результата

        if not game:
            return None
        else:
            # Возвращаем данные об игре, если она найдена
            return {
                "id": game.id,
                "steam_id": game.steam_id,
                "dmarket_id": str(game.dmarket_id).strip() if game.dmarket_id else None,
                "name": game.name,
            }

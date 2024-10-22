from app.database.models import async_session
from app.database.models import User, Game, Currency, Language, Item
from sqlalchemy import select
from datetime import datetime
from app.utils.errors import ErrorCode


# -------------------------------------------------SET--------------------------------------------------------


# SET USER
async def set_user(tg_id, username):
    async with async_session() as session:

        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(
                User(
                    tg_id=tg_id,
                    steam_id="",
                    username=username,
                    language=1,
                    currency=1,
                    favorite=[],
                    premium=False,
                    state={},
                )
            )
            await session.commit()
            return {"success": True}


# SET SETUP
async def set_setup(tg_id, language, currency, game):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        try:
            language_id = await session.scalar(
                select(Language.id).where(Language.language_code == language)
            )
            currency_id = await session.scalar(
                select(Currency.id).where(Currency.name == currency)
            )
            game_id = await session.scalar(select(Game.id).where(Game.name == game))

            user.language = language_id
            user.currency = currency_id
            user.state = {
                "sel_game": game_id,
                "inspected_item": None,
                "setup_complete": True,
            }
            await session.commit()
            return {"success": True}
        except:
            return {"success": False}


# SET INSPECTED ITEM
async def set_inspected_item(tg_id, item):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            current_state = user.state.copy() if user.state else {}
            current_state["inspected_item"] = item
            user.state = current_state
            await session.commit()
            return {"success": True}
        else:
            return {"success": False, "error": ErrorCode.USER_NOT_FOUND}


# RESET INSPECTED ITEM
async def reset_inspected_item(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            current_state = user.state.copy() if user.state else {}
            current_state["inspected_item"] = None
            user.state = current_state
            await session.commit()
            return {"success": True}
        else:
            return {"success": False, "error": ErrorCode.USER_NOT_FOUND}


async def add_item(hash_name, nameid, game):
    async with async_session() as session:
        new_item = Item(hash_name=hash_name, nameid=nameid, game=game)
        session.add(new_item)
        await session.commit()
        return {"status": "success", "message": "Item added successfully"}


# SET GAME
async def switch_game(tg_id, game):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        game_id = await session.scalar(select(Game.id).where(Game.name == game))

        if user:
            current_state = user.state.copy() if user.state else {}
            current_state["sel_game"] = game_id
            user.state = current_state
            await session.commit()
            return {"success": True}
        else:
            return {"success": False, "error": ErrorCode.USER_NOT_FOUND}


# SET FAVORITE
async def add_favorite(tg_id, app_id, hash_name):
    async with async_session() as session:

        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if user:
            current_items = user.favorite if user.favorite else []

            exists = any(
                item["game"] == app_id and item["hash_name"] == hash_name
                for item in current_items
            )

            if exists:
                return {"success": False, "error": ErrorCode.ITEM_EXISTS}

            new_favorite = {
                "game": app_id,
                "hash_name": hash_name,
                "added": datetime.now().isoformat(),
            }

            updated_favorite = current_items + [new_favorite]
            user.favorite = updated_favorite

            await session.commit()

            return {"success": True}
        else:
            return {"success": False, "error": ErrorCode.USER_NOT_FOUND}


async def remove_favorite(tg_id, app_id, hash_name):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if user:
            current_items = user.favorite if user.favorite else []

            # Ищем индекс элемента, который нужно удалить
            index_to_remove = next(
                (
                    index
                    for index, item in enumerate(current_items)
                    if item["game"] == app_id and item["hash_name"] == hash_name
                ),
                None,
            )

            if index_to_remove is not None:
                # Удаляем элемент из списка избранных
                del current_items[index_to_remove]
                user.favorite = current_items

                # Сохраняем изменения в базе данных
                await session.commit()

                return {"success": True}  # Элемент успешно удален
            else:
                return False  # Элемент не найден в избранном
        else:
            return {"success": False, "error": ErrorCode.USER_NOT_FOUND}


async def set_currency(tg_id: int, currency_id: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.tg_id == tg_id))
            user = result.scalars().first()
            user.currency = currency_id
        await session.commit()

async def set_language(tg_id: int, language_id: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.tg_id == tg_id))
            user = result.scalars().first()
            user.language = language_id
        await session.commit()


# -------------------------------------------------GET--------------------------------------------------------


# GET_STATE
async def get_state(tg_id):
    async with async_session() as session:
        # Получаем state пользователя
        state_result = await session.scalar(
            select(User.state).where(User.tg_id == tg_id)
        )

        # Получаем ID валюты из таблицы User
        currency_id = await session.scalar(
            select(User.currency).where(User.tg_id == tg_id)
        )

        # Получаем премиум статус пользователя
        premium = await session.scalar(select(User.premium).where(User.tg_id == tg_id))

        # Получаем язык пользователя
        language_code = await session.scalar(
            select(Language.language_code)
            .join(User, User.language == Language.id)
            .where(User.tg_id == tg_id)
        )

        # Если state не установлен, возвращаем setup_status как False
        if not state_result:
            data = {"setup_status": False}
            return data

        # Извлекаем данные из state
        setup_status = state_result.get("setup_complete")
        sel_game = state_result.get("sel_game")
        inspected_item = state_result.get("inspected_item")
        inspect_mode = state_result.get("inspect_mode")

        if not inspected_item:
            inspected_item = None

        if not sel_game:
            raise ValueError("sel_game is not set for the user.")

        # Получаем данные по выбранной игре
        game_data = await session.execute(
            select(Game.name, Game.id, Game.steam_id, Game.dmarket_id).where(
                Game.id == sel_game
            )
        )
        game_data = game_data.fetchone()

        if game_data is None:
            raise ValueError(f"No game found with id: {sel_game}")

        sel_game_name, sel_game_id, sel_game_steam_id, sel_game_dmarket_id = game_data
        sel_game_data = {
            "name": sel_game_name.strip(),
            "id": sel_game_id,
            "steam_id": sel_game_steam_id,
            "dmarket_id": sel_game_dmarket_id.strip(),
        }

        # Получаем имя валюты через join с таблицей Currency
        currency_name = await session.scalar(
            select(Currency.name)
            .join(User, User.currency == Currency.id)
            .where(User.tg_id == tg_id)
        )

        # Формируем результат для возврата
        data = {
            "inspect_mode": inspect_mode,
            "sel_game_data": sel_game_data,
            "inspected_item": inspected_item,
            "premium": premium,
            "setup_status": setup_status,
            "currency": currency_id,
            "currency_name": currency_name,
            "language": language_code,
        }

        return data


async def get_favorite(tg_id: int, app_id: int):

    async with async_session() as session:
        # Формируем запрос для получения пользователя по tg_id
        stmt = select(User).where(User.tg_id == tg_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        filtered_favorites = [
            item for item in user.favorite if item.get("game") == app_id
        ]

        if not filtered_favorites:
            return {"success": False, "error": ErrorCode.EMPTY_FAVORITE}
        return {"success": True, "data": filtered_favorites}


async def get_item(hash_name):
    async with async_session() as session:
        data = await session.scalar(select(Item).where(Item.hash_name == hash_name))

        if not data:
            return None
        else:
            return {
                "hash_name": data.hash_name,
                "nameid": data.nameid,
                "game": data.game,
            }


async def get_language():
    async with async_session() as session:
        data = await session.scalar(select(Language))

        if not data:
            return None
        else:
            return {
                "id": data.id,
                "language_code": data.language_code,
                "name": data.name,
            }


async def get_languages():
    async with async_session() as session:
        result = await session.scalars(select(Language))
        data = result.all()

        if not data:
            return None
        else:
            return [
                {
                    "id": language.id,
                    "name": language.name,
                    "language_code": language.language_code,
                }
                for language in data
            ]

async def get_currencies():
    async with async_session() as session:
        result = await session.scalars(select(Currency))
        data = result.all()

        if not data:
            return None
        else:
            return [{"id": Currency.id, "name": Currency.name} for Currency in data]


async def get_games():
    async with async_session() as session:
        result = await session.scalars(select(Game))
        data = result.all()

        if not data:
            return None
        else:
            return [
                {
                    "id": game.id,
                    "steam_id": game.steam_id,
                    "dmarket_id": game.dmarket_id,
                    "name": game.name,
                }
                for game in data
            ]


from sqlalchemy import select
from app.database.models import async_session, Currency


async def get_currency_ratio(currency_id: int):
    async with async_session() as session:
        # Выполняем запрос для получения объекта Currency по currency_id
        result = await session.scalar(
            select(Currency).where(Currency.id == currency_id)
        )

        # Проверяем, есть ли результат
        if result:
            return {
                "ratio": result.ratio,
                "time": result.time,
            }  # Возвращаем ratio и time
        else:
            return {"error": "Currency not found"}

import asyncio
from app.api.steam import get_price
from app.api.dmarket import get_dmarket_price
from app.utils.errors import get_error_message
from datetime import datetime
import app.database.requests as rq


async def compare_price(game_data, item, currency, currency_name):
    steam_id = game_data.get("steam_id")
    dmarket_id = game_data.get("dmarket_id")

    # Выполняем запросы параллельно
    steam_data_response, dmarket_data_response = await asyncio.gather(
        get_price(steam_id, item, currency), get_dmarket_price(dmarket_id, item)
    )

    # Проверяем успешность запроса к Steam
    if not steam_data_response.get("success", False):
        error_message = get_error_message(
            steam_data_response.get("error"), details=steam_data_response.get("details", "")
        )
        return {"success": False, "text": error_message}

    # Обрабатываем данные Steam
    steam_data = {
        "min_price": steam_data_response["data"].get("lowest_price"),
        "average_price": steam_data_response["data"].get("median_price"),
        "offers": steam_data_response["data"].get("volume"),
    }

    # Инициализируем данные DMarket, если данные пришли
    dmarket_data = None
    if dmarket_data_response:
        exchange_ratio = await rq.get_currency_ratio(currency)
        ratio = exchange_ratio.get("ratio", 1)  # Дефолтное значение 1 на случай ошибки
        converted_max_price = round(dmarket_data_response.get("max_price", 0) * ratio, 2)
        converted_min_price = round(dmarket_data_response.get("min_price", 0) * ratio, 2)
        converted_average_price = round(
            dmarket_data_response.get("average_price", 0) * ratio, 2
        )

        dmarket_data = {
            "min_price": dmarket_data_response.get("min_price"),
            "min_price_count": dmarket_data_response.get("min_price_count"),
            "max_price": dmarket_data_response.get("max_price"),
            "max_price_count": dmarket_data_response.get("max_price_count"),
            "offers": dmarket_data_response.get("total_offers"),
            "average_price": dmarket_data_response.get("average_price"),
            "converted_max_price": converted_max_price,
            "converted_min_price": converted_min_price,
            "converted_average_price": converted_average_price,
            "converted_ratio": round(ratio, 2),
            "exchange_time": datetime.fromisoformat(
                exchange_ratio.get("time")
            ).strftime("%d %B %Y, %H:%M"),
        }

    # Возвращаем структурированные данные
    return {
        "success": True,
        "steam_data": steam_data,
        "dmarket_data": dmarket_data,
    }

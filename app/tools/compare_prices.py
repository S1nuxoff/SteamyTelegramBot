import asyncio
from app.api.steam.requests import get_price
from app.api.dmarket.dmarket import get_dmarket_price
from app.utils.errors import get_error_message
from datetime import datetime
import app.database.requests as rq


async def compare_price(game_data, item, currency):
    steam_id = game_data.get("steam_id")
    dmarket_id = game_data.get("dmarket_id")

    exchange_ratio = await rq.get_currency_ratio(currency)
    ratio = exchange_ratio.get("ratio", 1)

    steam_data_response, dmarket_data_response = await asyncio.gather(
        get_price(steam_id, item, currency),
        get_dmarket_price(dmarket_id, item),
        # get_skinport_prices(steam_id, item)
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

    dmarket_data = None
    if dmarket_data_response:
        dmarket_converted_max_price = round(dmarket_data_response.get("max_price", 0) * ratio, 2)
        dmarket_converted_min_price = round(dmarket_data_response.get("min_price", 0) * ratio, 2)

        dmarket_converted_average_price = round(
            dmarket_data_response.get("average_price", 0) * ratio, 2
        )

        dmarket_data = {
            "min_price": dmarket_data_response.get("min_price"),
            "min_price_count": dmarket_data_response.get("min_price_count"),
            "max_price": dmarket_data_response.get("max_price"),
            "max_price_count": dmarket_data_response.get("max_price_count"),
            "offers": dmarket_data_response.get("total_offers"),
            "average_price": dmarket_data_response.get("average_price"),
            "converted_max_price": dmarket_converted_max_price,
            "converted_min_price": dmarket_converted_min_price,
            "converted_average_price": dmarket_converted_average_price,
            "converted_ratio": round(ratio, 2),
            "exchange_time": datetime.fromisoformat(
                exchange_ratio.get("time")
            ).strftime("%d %B %Y, %H:%M"),
        }
    skinport_data = None
    # if skinport_data_response:
    #     skinport_converted_max_price = round(dmarket_data_response.get("max", 0) * ratio, 2)
    #     skinport_converted_min_price = round(dmarket_data_response.get("min", 0) * ratio, 2)
    #     skinport_converted_avg_price = round(dmarket_data_response.get("median", 0) * ratio, 2)
    #
    #     skinport_data = {
    #         "min_price": skinport_data_response.get('min'),
    #         "max_price": skinport_data_response.get('max'),
    #         "average_price": skinport_data_response.get('median'),
    #         "offers": skinport_data_response.get('volume')
    #     }
    return {
        "success": True,
        "steam_data": steam_data,
        "dmarket_data": dmarket_data,
        "skinport_data": skinport_data
    }

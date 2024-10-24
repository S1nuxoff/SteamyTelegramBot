import aiohttp
import asyncio
from config import DMARKET_MARKET_ITEMS_URL


async def get_dmarket_price(game_id, item_name):
    currency_code = "USD"
    limit = 100
    url = DMARKET_MARKET_ITEMS_URL  # URL взят из конфигурационного файла

    params = {
        "gameId": game_id,
        "title": item_name,
        "limit": limit,
        "currency": currency_code,
        "orderBy": "price",
        "orderDir": "asc",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()  # Проверяем статус ответа
                data = await response.json()  # Дожидаемся получения JSON

                items = data.get("objects", [])

                if not items:
                    return {"error": "Предметы не найдены"}

                # Преобразуем цены в доллары и фильтруем по валюте
                prices = [
                    int(item["price"].get(currency_code, 0)) / 100
                    for item in items
                    if currency_code in item["price"]
                ]

                total_items = len(prices)

                if total_items == 0:
                    return {"error": "Цены не найдены"}

                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / total_items

                # Подсчет количества минимальных и максимальных цен
                min_price_count = prices.count(min_price)
                max_price_count = prices.count(max_price)

                prices_data = {
                    "min_price": min_price,
                    "min_price_count": min_price_count,
                    "max_price": max_price,
                    "max_price_count": max_price_count,
                    "average_price": round(avg_price, 2),
                    "total_offers": (
                        f"{total_items}+" if total_items >= limit else total_items
                    ),
                }

                return prices_data

    except aiohttp.ClientResponseError as err:
        return {"error": f"Ошибка ответа сервера: {str(err)}"}
    except aiohttp.ClientConnectionError as err:
        return {"error": f"Ошибка соединения: {str(err)}"}
    except asyncio.TimeoutError as err:
        return {"error": "Превышено время ожидания"}
    except Exception as err:
        return {"error": f"Неизвестная ошибка: {str(err)}"}

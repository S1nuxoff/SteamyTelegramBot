import aiohttp
from backend.config import DMARKET_MARKET_ITEMS_URL


async def get_dmarket_price(game_id, item):
    currency_code = "USD"
    limit = 100
    url = DMARKET_MARKET_ITEMS_URL
    params = {
        "gameId": game_id,
        "title": item,
        "limit": limit,
        "currency": currency_code,
        "orderBy": "price",
        "orderDir": "asc",
    }

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

            min_price_count = prices.count(min_price)
            max_price_count = prices.count(max_price)

            prices_data = {
                "min": min_price,
                "min_volume": min_price_count,
                "max": max_price,
                "max_volume": max_price_count,
                "avg": round(avg_price, 2),
                "volume": (
                    f"{total_items}+" if total_items >= limit else total_items
                ),
            }

            return prices_data

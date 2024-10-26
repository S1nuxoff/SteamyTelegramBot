import aiohttp
from backend.config import STEAM_PRICE_OVERVIEW_URL
from backend.utils.common import clean_price

async def get_price(appid, item):
    url = STEAM_PRICE_OVERVIEW_URL
    params = {
        "appid": appid,
        "market_hash_name": item,
        "currency": "USD",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                if data.get("success"):
                    lowest_price_str = data.get("lowest_price")
                    median_price_str = data.get("median_price")
                    volume = data.get("volume")

                    lowest_price = await clean_price(lowest_price_str)
                    median_price = await clean_price(median_price_str)
                    data = {
                        "lowest_price": lowest_price,
                        'median_price':median_price,
                        'volume': volume,
                    }
                    return {"success": True, "data": data}
                else:
                    return {"success": False}
    except aiohttp.ClientResponseError:
        return {"success": False}

import aiohttp
import asyncio
from backend.utils.common import clear_url
from backend.config import STEAM_PRICE_OVERVIEW_URL


async def verify_item(appid, item):
    name = await clear_url(item, appid)
    if name:
        url = STEAM_PRICE_OVERVIEW_URL
        params = {
            "appid": appid,
            "market_hash_name": name,
            "currency": "USD",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if data.get("success"):
                        return {"success": True, "data": name}
                    else:
                        return {"success": False}
        except aiohttp.ClientError:
            return {"success": False}
        except asyncio.TimeoutError:
            return {"success": False}
    else:
        return {"success": False}



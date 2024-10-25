import aiohttp
import asyncio
import re
import urllib.parse
from app.utils.common import clear_url
from app.utils.errors import ErrorCode
import app.database.requests as rq
from config import STEAM_PRICE_OVERVIEW_URL, STEAM_MARKET_LISTINGS_URL


async def get_price(appid, item, currency_id):
    url = STEAM_PRICE_OVERVIEW_URL
    params = {
        "appid": appid,
        "market_hash_name": item,
        "currency": currency_id,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                if data.get("success"):
                    return {"success": True, "data": data}
                else:
                    return {"success": False, "error": ErrorCode.NOT_FOUND}
    except aiohttp.ClientResponseError:
        return {"success": False, "error": ErrorCode.NOT_FOUND}
    except aiohttp.ClientConnectionError:
        return {"success": False, "error": ErrorCode.CONNECTION_ERROR}
    except asyncio.TimeoutError:
        return {"success": False, "error": ErrorCode.TIMEOUT}


async def item_exists(appid, item):
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
                        return {"success": False, "error": ErrorCode.NOT_FOUND}
        except aiohttp.ClientError:
            return {"success": False, "error": ErrorCode.NOT_FOUND}
        except asyncio.TimeoutError:
            return {"success": False, "error": ErrorCode.TIMEOUT}
    else:
        return {"success": False, "error": ErrorCode.INVALID_GAME}


regex = re.compile(r"Market_LoadOrderSpread\( (\d+) \)")

async def fetch_item_page(appid: int, market_hash_name: str, timeout: int = 10):
    encoded_name = urllib.parse.quote(market_hash_name)
    url = f"{STEAM_MARKET_LISTINGS_URL}{appid}/{encoded_name}"

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                html_data = await response.text()
    except aiohttp.ClientError:
        raise ConnectionError("Ошибка подключения")
    except asyncio.TimeoutError:
        raise TimeoutError("Время ожидания истекло")

    id_match = regex.search(html_data)

    if not id_match:
        return {"success": False, "error": ErrorCode.NOT_FOUND}

    nameid = int(id_match.group(1))
    return html_data, nameid, url




import aiohttp
import re
import urllib.parse
from config import STEAM_MARKET_LISTINGS_URL

regex = re.compile(r"Market_LoadOrderSpread\( (\d+) \)")

async def get_nameid(appid: int, market_hash_name: str, timeout: int = 10):
    encoded_name = urllib.parse.quote(market_hash_name)
    url = f"{STEAM_MARKET_LISTINGS_URL}{appid}/{encoded_name}"

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
        async with session.get(url) as response:
            response.raise_for_status()
            html_data = await response.text()

    id_match = regex.search(html_data)

    if not id_match:
        return {"success": False}

    nameid = int(id_match.group(1))

    return {'success': True, 'data': nameid}



import aiohttp
import re
import urllib.parse
from app.utils.common import clean_price, calculate_margin
import app.database.requests as rq
from backend.api import nameid_endpoint


regex = re.compile(r"Market_LoadOrderSpread\( (\d+) \)")


async def check_liquidity(appid, item, currency):
    encoded_market_hash_name = urllib.parse.quote(item)

    try:
        item_in_db = await rq.get_item(item)

        if not item_in_db:

            async with aiohttp.ClientSession() as session:
                async with session.get(
                        "http://185.93.6.180:8000/nameid",
                        params={"appid": appid, "items": item}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                    else:
                        data = {"success": False}

            nameid = data.get("data")

            await rq.add_item(item, nameid, appid)

        else:
            nameid = item_in_db.get("nameid")

            async with aiohttp.ClientSession() as session:
                async with session.get(
                        "http://185.93.6.180:8000/liquidity",
                        params={"nameid": nameid}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                    else:
                        data = {"success": False}
        return data

    except Exception as e:
        print(f"Error in check_liquidity: {str(e)}")
        raise

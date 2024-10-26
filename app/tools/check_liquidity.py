import aiohttp
import re
import urllib.parse
from app.utils.common import clean_price, calculate_margin
import app.database.requests as rq
from backend.api import nameid_endpoint
from config import ITEM_ORDERS_HISTOGRAM_URL, STEAM_BASE_URL

regex = re.compile(r"Market_LoadOrderSpread\( (\d+) \)")


async def get_liquidity(currency, nameid):
    item_orders_histogram_url = f"{ITEM_ORDERS_HISTOGRAM_URL}?country=USA&language=english&currency={currency}&item_nameid={nameid}&two_factor=0&norender=1"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(item_orders_histogram_url) as response:
                response.raise_for_status()
                item_orders_histogram_data = await response.json()

            item_lowest_sell_order_str = item_orders_histogram_data.get(
                "sell_order_price"
            )
            item_highest_buy_order_str = item_orders_histogram_data.get(
                "buy_order_price"
            )

            if not item_lowest_sell_order_str or not item_highest_buy_order_str:
                raise ValueError("Missing necessary pricing data from Steam.")

            item_lowest_sell_order = await clean_price(item_lowest_sell_order_str)
            item_highest_buy_order = await clean_price(item_highest_buy_order_str)

            (
                sell_order_after_commission,
                margin_value,
                margin_percentage,
            ) = await calculate_margin(item_lowest_sell_order, item_highest_buy_order)

            margin_status = "🟢" if margin_value > 0 else "🔴"

            data = {
                "highest_buy_order": item_highest_buy_order_str,
                "highest_sell_order_no_fee": sell_order_after_commission,
                "lowest_sell_order": item_lowest_sell_order_str,
                "margin_value": margin_value,
                "margin": margin_percentage,
                "margin_status": margin_status,
            }
            return data

        except aiohttp.ClientResponseError as e:
            print(f"HTTP error while fetching data: {e.status}")
            raise
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise


async def check_liquidity(appid, item, currency):
    encoded_market_hash_name = urllib.parse.quote(item)

    try:
        item_in_db = await rq.get_item(item)

        if not item_in_db:

            async with aiohttp.ClientSession() as session:
                async with session.get(
                        "http://185.93.6.180:8000/nameid",
                        params={"appid": appid, "item": item}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                    else:
                        data = {"success": False}

            nameid = data.get("data")

            await rq.add_item(item, nameid, appid)
            data = await get_liquidity(currency, nameid)

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

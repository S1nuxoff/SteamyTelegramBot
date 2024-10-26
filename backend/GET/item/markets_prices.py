import asyncio
import backend.database.requests as rq

from backend.GET.item.price import get_price
from backend.markets.dmarket.price import get_dmarket_price
from backend.markets.skinport.price import get_skinport_prices


async def get_markets_prices(appid, item):
    game_data = await rq.get_game_data(appid)
    dmarket_id = game_data.get("dmarket_id")

    steam_data_response, dmarket_data_response, skinport_data_response = await asyncio.gather(
        get_price(appid, item),
        get_dmarket_price(dmarket_id, item),
        get_skinport_prices(appid, item)
    )

    steam_data = None

    if steam_data_response:
        steam_data = {
            "market": "Steam",
            "min": steam_data_response["data"].get("lowest_price"),
            "avg": steam_data_response["data"].get("median_price"),
            "volume": steam_data_response["data"].get("volume"),
        }

    dmarket_data = None

    if dmarket_data_response:
        dmarket_data = {
            "market": "DMarket",
            "min": dmarket_data_response.get('min'),
            "avg": dmarket_data_response.get('avg'),
            "volume": dmarket_data_response.get('volume'),
        }

    skinport_data = None

    if skinport_data_response:
        skinport_data = {
            "market": "Skinport",
            "min": skinport_data_response.get('min'),
            "avg": skinport_data_response.get('avg'),
            "volume": skinport_data_response.get('volume'),
        }


    markets_data = []

    if steam_data:
        markets_data.append(steam_data)

    if dmarket_data:
        markets_data.append(dmarket_data)

    if skinport_data:
        markets_data.append(skinport_data)

    result = {
        "success": True,
        "markets": markets_data
    }

    return result

import aiohttp
import asyncio
import re
import urllib.parse
from app.utils.steam import clear_url, extract_data_from_html, filter_price_data
from app.utils.errors import ErrorCode
import app.database.requests as rq
from config import STEAM_PRICE_OVERVIEW_URL, STEAM_MARKET_LISTINGS_URL


async def get_price(appid, item, currency_id):
    url = STEAM_PRICE_OVERVIEW_URL  # URL взят из конфигурационного файла
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
        url = STEAM_PRICE_OVERVIEW_URL  # URL взят из конфигурационного файла
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


async def get_item_html(appid, market_hash_name, period, currency_id):
    encoded_market_hash_name = urllib.parse.quote(market_hash_name)
    base_url = f"{STEAM_MARKET_LISTINGS_URL}{appid}/{encoded_market_hash_name}"  # URL взят из конфигурационного файла

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url) as response:
                response.raise_for_status()
                html_data = await response.text()
    except aiohttp.ClientError:
        return {"success": False, "error": ErrorCode.CONNECTION_ERROR}
    except asyncio.TimeoutError:
        return {"success": False, "error": ErrorCode.TIMEOUT}

    id_match = regex.search(html_data)

    if not id_match:
        return {"success": False, "error": ErrorCode.NOT_FOUND}

    nameid = int(id_match.group(1))

    if not await rq.get_item(market_hash_name):
        await rq.add_item(market_hash_name, nameid, appid)

    dates, prices, sales = await extract_data_from_html(html_data)
    filtered_dates, filtered_prices, used_period = await filter_price_data(
        dates, prices, period
    )

    filtered_sales = (
        [sale for sale, date in zip(sales, dates) if date >= filtered_dates[0]]
        if filtered_dates
        else []
    )

    avg_price = (
        round(sum(filtered_prices) / len(filtered_prices), 2)
        if filtered_prices
        else 0.00
    )
    max_price = round(max(filtered_prices), 2) if filtered_prices else 0
    min_price = round(min(filtered_prices), 2) if filtered_prices else 0
    total_sales = round(sum(filtered_sales), 2) if filtered_sales else 0

    # Определение допустимой погрешности
    tolerance = 0.02

    # Подсчёт количества продаж по минимальной, средней и максимальной цене
    def count_sales_within_tolerance(price, tolerance, prices):
        return sum(1 for p in prices if price - tolerance <= p <= price + tolerance)

    sales_at_min_price = count_sales_within_tolerance(
        min_price, tolerance, filtered_prices
    )
    sales_at_avg_price = count_sales_within_tolerance(
        avg_price, tolerance, filtered_prices
    )
    sales_at_max_price = count_sales_within_tolerance(
        max_price, tolerance, filtered_prices
    )

    if used_period != period:
        message = (
            "😊 Oops! No data available for the selected period.\n"
            f"🔄 We've used the period: {used_period.capitalize()}."
        )
    else:
        message = "✅ Data loaded successfully"

    data = {
        "message": message,
        "max_price": max_price,
        "min_price": min_price,
        "avg_price": avg_price,
        "total_sales": total_sales,
        "sales_at_min_price": sales_at_min_price,
        "sales_at_avg_price": sales_at_avg_price,  # Добавлено количество продаж по средней цене
        "sales_at_max_price": sales_at_max_price,
        "dates": filtered_dates,
        "prices": filtered_prices,
        "period": period,
    }
    return data

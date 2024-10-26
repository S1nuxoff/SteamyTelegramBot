import re
import json
import aiohttp
import urllib.parse
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any

from backend.config import STEAM_MARKET_LISTINGS_URL

regex = re.compile(r"Market_LoadOrderSpread\( (\d+) \)")


async def extract_sales_history(html_data):
    pattern = r"var line1\s*=\s*(\[.*?\]);"
    match = re.search(pattern, html_data, re.MULTILINE | re.DOTALL)

    if not match:
        return None, None, None
    try:
        data_str = match.group(1)
        data_list = json.loads(data_str)
    except (json.JSONDecodeError, SyntaxError) as e:
        print(f"Error parsing data: {e}")
        return None, None, None

    dates = []
    prices = []
    sales = []

    for entry in data_list:
        try:
            date_str = entry[0]
            price = float(entry[1])
            sales_volume = int(entry[2])

            try:
                date_obj = datetime.strptime(date_str, "%b %d %Y %H: +0")
            except ValueError:
                date_obj = datetime.strptime(date_str, "%b %d %Y %H:%M")

            dates.append(date_obj)
            prices.append(price)
            sales.append(sales_volume)

        except (ValueError, IndexError) as e:
            print(f"Error processing entry: {entry}, error: {e}")
            continue

    return dates, prices, sales


async def filter_sales_history(dates: List[datetime], prices: List[float], period: str) -> Tuple[
    List[datetime], List[float], str]:
    periods = ["day", "week", "month", "lifetime"]
    period_deltas = {
        "day": timedelta(days=1),
        "week": timedelta(weeks=1),
        "month": timedelta(days=30),
        "all_time": None,
    }
    try:
        start_index = periods.index(period)
    except ValueError:

        start_index = 0
    now = datetime.now()
    for current_period in periods[start_index:]:
        if current_period == "lifetime":
            filtered_dates = dates.copy()
            filtered_prices = [round(price, 2) for price in prices]
        else:
            delta = period_deltas[current_period]
            start_date = now - delta
            filtered_dates = [date for date in dates if date >= start_date]
            filtered_prices = [
                round(prices[i], 2)
                for i, date in enumerate(dates)
                if date >= start_date
            ]
        if filtered_prices:
            return filtered_dates, filtered_prices, current_period
    return [], [], periods[-1]


async def extract_and_filter_sales_history(html_data: str, period: str) -> Dict[str, Any]:
    dates, prices, sales = await extract_sales_history(html_data)

    if not all([dates, prices, sales]):
        return {"Success": False, "error": "Failed to extract sales history."}
    filtered_dates, filtered_prices, filter_period = await filter_sales_history(dates, prices, period)
    if filtered_dates:
        first_date = filtered_dates[0]
        filtered_sales = [sale for sale, date in zip(sales, dates) if date >= first_date]
    else:
        filtered_sales = []
    return {
        "Success": True,
        "sales": {
            "filter_period": filter_period,
            "filtered_dates": filtered_dates,
            "filtered_prices": filtered_prices,
            "filtered_sales": filtered_sales
        }
    }


def count_sales_within_tolerance(price: float, tolerance: float, prices: List[float]) -> int:
    return sum(1 for p in prices if price - tolerance <= p <= price + tolerance)


def compute_statistics(filtered_prices: List[float], filtered_sales: List[int], tolerance: float = 0.02) -> Tuple[
    float, int, float, int, float, int, float]:
    if not filtered_prices:
        return 0.00, 0, 0.00, 0, 0.00, 0, 0.00
    avg_price = round(sum(filtered_prices) / len(filtered_prices), 2)
    avg_volume = count_sales_within_tolerance(avg_price, tolerance, filtered_prices)
    max_price = round(max(filtered_prices), 2)
    max_volume = count_sales_within_tolerance(max_price, tolerance, filtered_prices)
    min_price = round(min(filtered_prices), 2)
    min_volume = count_sales_within_tolerance(min_price, tolerance, filtered_prices)
    volume = round(sum(filtered_sales), 2)

    return avg_price, avg_volume, max_price, max_volume, min_price, min_volume, volume


async def get_sales_history(appid: int, market_hash_name: str, period: str, timeout=10) -> Dict[str, Any]:
    encoded_name = urllib.parse.quote(market_hash_name)
    url = f"{STEAM_MARKET_LISTINGS_URL}{appid}/{encoded_name}"

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
        async with session.get(url) as response:
            response.raise_for_status()
            html_data = await response.text()

    sales_data = await extract_and_filter_sales_history(html_data, period)
    if not sales_data.get("Success"):
        return sales_data

    sales = sales_data.get('sales')
    filter_period = sales.get('filter_period')
    filtered_dates = sales.get('filtered_dates')
    filtered_prices = sales.get('filtered_prices')
    filtered_sales = sales.get('filtered_sales')
    avg, avg_volume, max_price, max_volume, min_price, min_volume, volume = compute_statistics(filtered_prices,
                                                                                               filtered_sales)
    data = {
        "success": True,
        "data": {
            "market_hash_name": market_hash_name,
            "market_page": url,
            "filter_period": filter_period,
            "sales": {
                "min": min_price,
                "min_volume": min_volume,
                "max": max_price,
                "max_volume": max_volume,
                "avg": avg,
                "avg_volume": avg_volume,
                "volume": volume,
                "dates": filtered_dates,
                "prices": filtered_prices,
            }

        }
    }
    return data

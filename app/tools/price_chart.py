from datetime import datetime
import platform
import aiohttp
import app.database.requests as rq

from app.utils.charts.price_chart import create_price_chart


async def price_chart(appid, inspected_item, period, currency_id, currency_name):

    API_URL = "http://185.93.6.180:8000/sales_history"

    exchange_ratio = await rq.get_currency_ratio(currency_id)
    ratio = exchange_ratio.get("ratio", 1)
    ratio_time = exchange_ratio.get("time")

    async with aiohttp.ClientSession() as session:
        async with session.get(
                API_URL,
                params={"appid": appid, "items": inspected_item, "period": period}
        ) as response:
            if response.status == 200:
                data = await response.json()
            else:
                data = {"success": False}

    if not data.get("success"):
        error_message = data.get("error", "Unknown error occurred while fetching sales history.")
        return {"Success": False, "error": error_message}

    sales = data["data"]["sales"]
    filter_period = data["data"]["filter_period"]

    # Convert date strings to datetime objects
    dates = [datetime.fromisoformat(date) for date in sales["dates"]]
    prices = sales["prices"]

    chart_path = await create_price_chart(dates, prices, inspected_item, period, currency_name, ratio)

    report = {
        "max": round(sales["max"] * ratio, 2),
        "max_volume": sales["max_volume"],
        "min": round(sales["min"] * ratio, 2),
        "min_volume": sales["min_volume"],
        "avg": round(sales["avg"] * ratio, 2),
        "avg_volume": sales["avg_volume"],
        "volume": sales["volume"],
        "converted_ratio": round(ratio,2),
        "exchange_time": ratio_time,
        "filter_period": filter_period,
        "chart_path": chart_path,
    }
    return {"Success": True, "report": report}

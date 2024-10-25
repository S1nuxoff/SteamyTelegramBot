from datetime import datetime
import platform

from app.api.steam.sales import get_sales_history
from app.utils.charts.price_chart import create_price_chart


async def price_chart(appid, inspected_item, period, currency_id):
    data = await get_sales_history(appid, inspected_item, period, currency_id)

    if not data.get("Success"):
        error_message = data.get("error", "Unknown error occurred while fetching sales history.")

        return {"Success": False, "error": error_message}

    sales = data["data"]["sales"]

    filter_period = data["data"]["filter_period"]
    ratio = data["data"]["ratio"]
    exchange_time = data["data"]["ratio_time"]

    dt_object = datetime.fromisoformat(exchange_time)

    if platform.system() == "Windows":
        formatted_exchange_time = dt_object.strftime("%b %#d, %Y, %I:%M %p")
    else:
        formatted_exchange_time = dt_object.strftime("%b %-d, %Y, %I:%M %p")

    dates = sales["dates"]
    prices = sales["prices"]

    symbol = "$"

    chart_path = await create_price_chart(dates, prices, inspected_item, period, symbol)

    converted_ratio = round(ratio, 2)

    report = {
        "max": sales["max"],
        "max_volume": sales["max_volume"],
        "min": sales["min"],
        "min_volume": sales["min_volume"],
        "avg": sales["avg"],
        "avg_volume": sales["avg_volume"],
        "volume": sales["volume"],
        "converted_ratio": converted_ratio,
        "exchange_time": formatted_exchange_time,
        "filter_period": filter_period,
        "chart_path": chart_path,
    }
    return {"Success": True, "report": report}

import re
import urllib.parse
import json
from datetime import datetime, timedelta
from config import steam_commission_rate


async def is_url(url):
    url_pattern = re.compile(
        r"^(https?:\/\/)?"
        r"(([A-Za-z0-9-]+\.)+[A-Za-z]{2,})"
        r"(\/[A-Za-z0-9-._~:/?#\[\]@!$&\'()*+,;=%]*)?$"
    )
    return re.match(url_pattern, url) is not None


async def clear_url(url, appid):

    if not await is_url(url):
        return url

    appid_pattern = r"/listings/(\d+)/([^/?#]+)"
    match = re.search(appid_pattern, url)

    url_appid = int(match.group(1))
    print(url_appid)

    if url_appid != appid:
        return False
    else:
        encoded_item = match.group(2)
        encoded_item = encoded_item.split("https://")[
            0
        ]  # Clean up in case of URL fragments
        decoded_item = urllib.parse.unquote(encoded_item)
        return decoded_item


async def extract_data_from_html(html_data):

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


async def filter_price_data(dates, prices, period):
    periods = ["day", "week", "month", "lifetime"]
    period_deltas = {
        "day": timedelta(days=1),
        "week": timedelta(weeks=1),
        "month": timedelta(days=30),
        "lifetime": None,
    }

    # Determine the starting index based on the selected period
    try:
        start_index = periods.index(period)
    except ValueError:
        # If the provided period is not recognized, default to the smallest period
        start_index = 0

    now = datetime.now()

    for current_period in periods[start_index:]:
        if current_period == "lifetime":
            # No filtering; use all data
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
            # Data found; return the results along with the current period
            return filtered_dates, filtered_prices, current_period

    return [], [], periods[-1]


async def clean_price(price_str):
    clean_str = re.sub(
        r"[^\d.,]", "", price_str
    )  # Remove any non-numeric characters except commas and dots
    clean_str = clean_str.replace(",", ".")  # Replace commas with dots
    clean_str = clean_str.rstrip(".")  # Remove any trailing dot
    return float(clean_str)


async def calculate_margin(item_lowest_sell_order, item_highest_buy_order):

    sell_order_after_commission = round(
        item_lowest_sell_order * (1 - steam_commission_rate), 2
    )
    margin_value = round(sell_order_after_commission - item_highest_buy_order, 2)
    margin_percentage = round(
        (margin_value / item_highest_buy_order) * 100
    )  # Округляем до целого числа
    margin_status = "🟢" if margin_value > 0 else "🔴"
    return sell_order_after_commission, margin_value, margin_percentage, margin_status

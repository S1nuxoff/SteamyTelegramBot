import re
import urllib.parse
import json
from datetime import datetime, timedelta
from config import steam_commission_rate
# from app.api.steam import fetch_item_page


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
    if url_appid != appid:
        return False
    else:
        encoded_item = match.group(2)
        encoded_item = encoded_item.split("https://")[
            0
        ]
        decoded_item = urllib.parse.unquote(encoded_item)
        return decoded_item


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

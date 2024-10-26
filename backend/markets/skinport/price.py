import requests
import time
from backend.config import SKINPORT_MARKET_ITEMS_URL

# Initialize cache
cache = {}

async def get_skinport_prices(app_id, item):
    current_time = time.time()
    # Check if we have cached data for this app_id
    if app_id in cache:
        cached_time, response = cache[app_id]
        # If cached data is less than 5 minutes old (300 seconds)
        if current_time - cached_time < 300:
            pass  # Use cached response
        else:
            # Fetch new data and update cache
            response = requests.get(SKINPORT_MARKET_ITEMS_URL, params={
                "app_id": app_id,
                "currency": "USD",
                "tradable": 0
            }).json()
            cache[app_id] = (current_time, response)
    else:
        # Fetch data and add to cache
        response = requests.get(SKINPORT_MARKET_ITEMS_URL, params={
            "app_id": app_id,
            "currency": "USD",
            "tradable": 0
        }).json()
        cache[app_id] = (current_time, response)

    for market_item in response:
        if market_item.get('market_hash_name') == item:
            result = {
                'page': market_item.get('item_page'),
                'min': market_item.get('min_price'),
                'avg': market_item.get('median_price'),
                'volume': market_item.get('quantity')
            }
            print(result)
            return result
    return None

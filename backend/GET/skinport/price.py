import requests
from backend.config import SKINPORT_MARKET_ITEMS_URL


async def get_skinport_prices(app_id, item):
    response = requests.get(SKINPORT_MARKET_ITEMS_URL, params={
        "app_id": app_id,
        "currency": "USD",
        "market_hash_name": item
    }).json()

    if response and isinstance(response, list):
        item_data = response[0]
        last_24_hours = item_data.get('last_24_hours', {})
        # Prepare the result
        result = {
            'min': last_24_hours.get('min'),
            'avg': last_24_hours.get('median'),
            'volume': last_24_hours.get('volume')
        }

        return result
    else:
        return None

import requests


def get_skinport_prices(app_id, market_hash_name):
    # Make a request to the Skinport API with app_id and market_hash_name
    response = requests.get("https://api.skinport.com/v1/sales/history", params={
        "app_id": app_id,
        "currency": "USD",
        "market_hash_name": market_hash_name
    }).json()

    if response and isinstance(response, list):
        # Extract relevant fields
        item_data = response[0]
        item_page = f"https://skinport.com/item/{market_hash_name.replace(' ', '-').replace('|', '').lower()}"
        last_24_hours = item_data.get('last_24_hours', {})

        # Prepare the result
        result = {
            'item_page': item_page,
            'last_24_hours': {
                'min': last_24_hours.get('min'),
                'median': last_24_hours.get('median'),
                'volume': last_24_hours.get('volume')
            }
        }
        return result
    else:
        return None


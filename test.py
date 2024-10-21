import requests

url = "https://api.shadowpay.com/api/v1/search_items_by_list_names"
headers = {
    "Authorization": "Bearer d55ae72039d217fa7320b87ba916c3fb",  # Убедитесь, что токен актуален
    "Accept": "application/json",
}

querystring = {
    "project": "csgo",
    "steam_market_hash_name": "AK-47 | Slate (Field-Tested)",
    "to": "2024-10-20",
}

response = requests.get(url, headers=headers, params=querystring)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Ошибка: {response.status_code}, сообщение: {response.text}")

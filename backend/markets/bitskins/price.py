import aiohttp
import asyncio
import json

auth_key = '320a614bf50cefa22e5eba701fc540eb095d7bace7e2e28647b83ed03edc96bd'  # Замените на ваш API ключ

# import requests
# import json
#
#
# data = {
#   "where": {
#     "app_id": 730,
#     "skin_name": "Operation Breakout Weapon Case"
#   },
#   "limit": 30
# }
#
# headers = {'x-apikey': auth_key}
# res = requests.post('https://api.bitskins.com/market/search/skin_name', headers=headers, json=data)
# response = json.loads(res.text)
# print(response)
#


async def get_bitskins_price(game_id: int, item: str):
    search_url = 'https://api.bitskins.com/market/search/skin_name'
    pricing_url = 'https://api.bitskins.com/market/pricing/list'

    search_data = {
        "where": {
            "app_id": game_id,
            "skin_name": item
        },
        "limit": 30
    }

    pricing_data_template = {
        "app_id": game_id,
        "skin_id": 0  # Это значение будет заменено на реальный ID
    }

    headers = {'x-apikey': auth_key}

    async with aiohttp.ClientSession() as session:
        try:
            # Первый запрос: поиск скина
            async with session.post(search_url, headers=headers, json=search_data, timeout=10) as search_response:
                search_response.raise_for_status()  # Проверка на успешность запроса
                search_result = await search_response.json()

                if not search_result:
                    print(f"Скин '{item}' не найден для game_id {game_id}.")
                    return

                # Предполагается, что ответ — это список словарей
                first_item = search_result[0]
                skin_id = first_item.get('id')
                skin_name = first_item.get('name')
                print(skin_name)

                if not skin_id:
                    print("Не удалось получить 'id' скина из первого результата.")
                    return

                print(f"Найден скин: {first_item.get('name')} (ID: {skin_id})")


            pricing_data = pricing_data_template.copy()
            pricing_data["skin_id"] = skin_id

            async with session.post(pricing_url, headers=headers, json=pricing_data, timeout=10) as pricing_response:
                pricing_response.raise_for_status()
                pricing_result = await pricing_response.json()

                print(json.dumps(pricing_result, indent=4, ensure_ascii=False))
                print(skin_name)
                print(skin_id)

        except aiohttp.ClientError as e:
            print(f"HTTP ошибка: {e}")
        except asyncio.TimeoutError:
            print("Запрос превысил время ожидания.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")


# Пример использования функции
async def main():
    game_id = 730  # Пример: CS:GO
    item = "Operation Breakout Weapon Case"

    await get_bitskins_price(game_id, item)


if __name__ == "__main__":
    asyncio.run(main())

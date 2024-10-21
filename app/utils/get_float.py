import aiohttp
import asyncio


async def get_float_data(item_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.csgofloat.xyz/?item_url={item_url}"
            ) as response:
                response.raise_for_status()
                data = await response.json()

                if data.get("success"):
                    item_info = data.get("iteminfo", {})
                    return {
                        "origin": item_info.get("origin"),
                        "paint_seed": item_info.get("paintseed"),
                        "paint_index": item_info.get("paintindex"),
                        "float_value": item_info.get("floatvalue"),
                    }
                else:
                    error_message = data.get("error", "Unknown error")
                    raise Exception(f"Error in response: {error_message}")

    except aiohttp.ClientError as e:
        raise Exception(f"Error fetching float data: {e}")


# Example of how to call the async function
async def main():
    await get_float_data(
        "steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20M5383580983543635881A23316542101D17167834902600010579"
    )


# Running the async function
asyncio.run(main())

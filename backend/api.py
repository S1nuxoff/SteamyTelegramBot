from fastapi import FastAPI, Query
from backend.GET.steam.price import get_price
from backend.GET.steam.sales_history import get_sales_history
from backend.GET.steam.verify_item import verify_item
from backend.GET.steam.liquidity import get_liquidity
from backend.GET.steam.nameid import get_nameid
from backend.GET.general.float import get_float
from backend.POST.update_currencies import update_currencies
from backend.GET.general.markets_prices import get_markets_prices

app = FastAPI()

@app.get("/price")
async def price_endpoint(appid: int, item: str):
    result = await get_price(appid, item)
    return result

@app.get("/sales_history")
async def sales_history_endpoint(
    appid: int,
    item: str,
        period: str = Query("week", pattern="^(day|week|month|lifetime)$"),
):
    result = await get_sales_history(appid, item, period)
    return result

@app.get("/verify_item")
async def verify_item_endpoint(appid: int, item: str):
    result = await verify_item(appid, item)
    return result

@app.get("/liquidity")
async def liquidity_endpoint(nameid: int):
    result = await get_liquidity(nameid)
    return result

@app.get("/nameid")
async def nameid_endpoint(appid: int, item: str):
    result = await get_nameid(appid, item)
    return result

@app.get("/float")
async def float_endpoint(rungame_url: str):
    result = await get_float(rungame_url)
    return result

@app.get("/update_currencies")
async def update_currencies_endpoint():
    return await update_currencies()

@app.get("/update_currencies")
async def update_currencies_endpoint():
    return await update_currencies()


@app.get("/market_prices")
async def market_prices(appid: int, item: str):
    result = await get_markets_prices(appid, item)
    return result
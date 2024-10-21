from fastapi import FastAPI, HTTPException
import asyncio
from app.api.steam import get_price, item_exists, get_item_html
from app.utils.price_chart import price_chart
from app.utils.errors import ErrorCode

app = FastAPI()


@app.get("/price/")
async def get_price_endpoint(appid: int, item: str, currency_id: int):
    result = await get_price(appid, item, currency_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail="Item not found")
    return result["data"]


@app.get("/item_exists/")
async def item_exists_endpoint(appid: int, item: str):
    result = await item_exists(appid, item)
    if not result["success"]:
        raise HTTPException(status_code=404, detail="Item not found")
    return result["data"]


@app.get("/item_data/")
async def get_item_html_endpoint(appid: int, item: str, period: str, currency_id: int):
    result = await get_item_html(appid, item, period, currency_id)
    if result.get("error") == ErrorCode.NOT_FOUND:
        raise HTTPException(status_code=404, detail="Data not found")
    if result.get("error") == ErrorCode.TIMEOUT:
        raise HTTPException(status_code=504, detail="Request timeout")
    return result


@app.get("/price_chart/")
async def price_chart(appid, inspected_item, period, currency_id):
    result = await get_item_html(appid, inspected_item, period, currency_id)
    if result.get("error") == ErrorCode.NOT_FOUND:
        raise HTTPException(status_code=404, detail="Data not found")
    if result.get("error") == ErrorCode.TIMEOUT:
        raise HTTPException(status_code=504, detail="Request timeout")
    return result

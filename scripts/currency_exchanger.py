import aiohttp
import asyncio
import re
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import BigInteger, JSON, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Модель для таблицы Currency
class Base(DeclarativeBase):
    pass


class Currency(Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    ratio: Mapped[float] = mapped_column()
    time: Mapped[str] = mapped_column()


# Настройка подключения к базе данных PostgreSQL
DATABASE_URL = "postgresql+asyncpg://steamy:Afynjv228@185.93.6.180:5432/steamy_db"
engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

CURRENCY_ID_MAP = {1: "USD", 5: "RUB", 6: "PLN", 18: "UAH"}


async def fetch_price(session, url, params):
    try:
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            if data.get("success"):
                return data.get("lowest_price")
            else:
                return None
    except Exception:
        return None


def parse_price(price_str):
    price_str_nospace = price_str.replace(" ", "")
    match = re.search(r"[\d.,]+", price_str_nospace)
    if not match:
        raise ValueError(f"Cannot parse price string: {price_str}")
    amount_str = match.group(0)
    num_commas = amount_str.count(",")
    num_dots = amount_str.count(".")
    if num_commas > num_dots:
        amount_str_clean = amount_str.replace(".", "").replace(",", ".")
    else:
        amount_str_clean = amount_str.replace(",", "")
    try:
        amount = float(amount_str_clean)
    except ValueError:
        raise ValueError(f"Cannot convert amount to float: {amount_str_clean}")
    return amount


async def update_currency(session, currency_code, ratio, request_time):
    async with session.begin():
        stmt = select(Currency).where(Currency.name == currency_code)
        result = await session.execute(stmt)
        currency = result.scalar_one_or_none()

        if currency:
            currency.ratio = ratio
            currency.time = request_time
            await session.commit()
        else:
            print(f"Currency {currency_code} not found in database.")


async def get_price():
    appid = 730
    item = "StatTrak™ AK-47 | Redline (Field-Tested)"
    currency_ids = [1, 5, 6, 18]
    url = "https://steamcommunity.com/market/priceoverview/"
    params_base = {
        "appid": appid,
        "market_hash_name": item,
    }
    async with aiohttp.ClientSession() as http_session, async_session() as db_session:
        tasks = []
        for currency_id in currency_ids:
            params = params_base.copy()
            params["currency"] = currency_id
            tasks.append(fetch_price(http_session, url, params))
        results = await asyncio.gather(*tasks)

        lowest_prices = {}
        for currency_id, price_str in zip(currency_ids, results):
            if price_str:
                try:
                    amount = parse_price(price_str)
                    currency_code = CURRENCY_ID_MAP.get(currency_id, "UNKNOWN")
                    lowest_prices[currency_id] = {
                        "amount": amount,
                        "currency_code": currency_code,
                    }
                except ValueError:
                    pass

        base_price_info = lowest_prices.get(1)
        if not base_price_info:
            return {"success": False, "error": "Base price not available"}

        base_amount = base_price_info["amount"]
        request_time = datetime.now().isoformat()

        for currency_id in [5, 6, 18]:
            price_info = lowest_prices.get(currency_id)
            if price_info:
                ratio = price_info["amount"] / base_amount
                await update_currency(
                    db_session, price_info["currency_code"], ratio, request_time
                )

    return {"success": True, "request_time": request_time}


# Пример использования
if __name__ == "__main__":
    asyncio.run(get_price())

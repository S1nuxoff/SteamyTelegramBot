import aiohttp
import asyncio
import re
import logging
from datetime import datetime
from typing import Optional, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Модель для таблицы Currency
class Base(DeclarativeBase):
    pass


class Currency(Base):
    __tablename__ = "currencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    ratio: Mapped[float] = mapped_column(default=1.0)
    time: Mapped[str] = mapped_column()


# Настройка подключения к базе данных PostgreSQL
DATABASE_URL = "postgresql+asyncpg://steamy:Afynjv228@185.93.6.180:5432/steamy_db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

CURRENCY_ID_MAP: Dict[int, str] = {1: "USD", 5: "RUB", 6: "PLN", 18: "UAH"}


async def fetch_price(session: aiohttp.ClientSession, url: str, params: Dict) -> Optional[str]:
    """
    Fetches the lowest price from the Steam Community Market API.
    """
    try:
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            if data.get("success"):
                price = data.get("lowest_price")
                logger.debug(f"Fetched price for {params.get('currency')}: {price}")
                return price
            else:
                logger.warning(f"API response not successful for params: {params}")
                return None
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error occurred: {e}")
        return None
    except asyncio.TimeoutError:
        logger.error("Request timed out.")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return None


def parse_price(price_str: str) -> float:
    """
    Parses a price string and converts it to a float.
    Supports formats like "1,234.56" or "1.234,56".
    """
    price_str_nospace = price_str.replace(" ", "")
    match = re.search(r"[\d.,]+", price_str_nospace)
    if not match:
        raise ValueError(f"Cannot parse price string: {price_str}")

    amount_str = match.group(0)
    logger.debug(f"Parsing price string: {amount_str}")

    # Determine the decimal separator
    if amount_str.count(",") > amount_str.count("."):
        # Assume ',' is decimal separator
        amount_str_clean = amount_str.replace(".", "").replace(",", ".")
    else:
        # Assume '.' is decimal separator
        amount_str_clean = amount_str.replace(",", "")

    try:
        amount = float(amount_str_clean)
        logger.debug(f"Converted amount: {amount}")
        return amount
    except ValueError:
        raise ValueError(f"Cannot convert amount to float: {amount_str_clean}")


async def update_currencies(
        session: AsyncSession,
        currency_ratios: Dict[str, float],
        request_time: str
) -> None:
    """
    Updates multiple currency ratios in the database within a single transaction.
    """
    try:
        async with session.begin():
            stmt = select(Currency).where(Currency.name.in_(currency_ratios.keys()))
            result = await session.execute(stmt)
            currencies = result.scalars().all()

            if not currencies:
                logger.warning("No currencies found to update.")
                return

            for currency in currencies:
                new_ratio = currency_ratios.get(currency.name)
                if new_ratio is not None:
                    logger.debug(f"Updating {currency.name}: {currency.ratio} -> {new_ratio}")
                    currency.ratio = new_ratio
                    currency.time = request_time

    except Exception as e:
        logger.exception(f"Failed to update currencies: {e}")
        raise  # Re-raise exception after logging


async def get_prices_and_update_db() -> Dict[str, Optional[str]]:
    """
    Fetches prices for specified currencies and updates the database with their ratios.
    """
    appid = 730
    item = "AWP | Crakow! (Minimal Wear)"
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

        results = await asyncio.gather(*tasks, return_exceptions=True)

        lowest_prices: Dict[int, str] = {}
        for currency_id, result in zip(currency_ids, results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching price for currency ID {currency_id}: {result}")
                continue

            price_str = result
            if price_str:
                try:
                    amount = parse_price(price_str)
                    currency_code = CURRENCY_ID_MAP.get(currency_id, "UNKNOWN")
                    lowest_prices[currency_id] = amount
                    logger.info(f"Fetched {currency_code}: {amount}")
                except ValueError as ve:
                    logger.error(f"Error parsing price for currency ID {currency_id}: {ve}")

        base_amount = lowest_prices.get(1)
        if not base_amount:
            logger.error("Base price (USD) not available. Aborting update.")
            return {"success": False, "error": "Base price not available"}

        request_time = datetime.utcnow().isoformat()
        currency_ratios = {}
        for currency_id in [5, 6, 18]:
            amount = lowest_prices.get(currency_id)
            if amount:
                currency_code = CURRENCY_ID_MAP.get(currency_id, "UNKNOWN")
                ratio = amount / base_amount
                currency_ratios[currency_code] = ratio
                logger.info(f"Calculated ratio for {currency_code}: {ratio}")

        if currency_ratios:
            try:
                await update_currencies(db_session, currency_ratios, request_time)
                logger.info("Currencies updated successfully.")
            except Exception as e:
                logger.error(f"Failed to update currencies in DB: {e}")
                return {"success": False, "error": "Database update failed"}

        return {"success": True, "request_time": request_time}


async def main():
    result = await get_prices_and_update_db()
    if result["success"]:
        logger.info(f"Update successful at {result['request_time']}")
    else:
        logger.error(f"Update failed: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(main())

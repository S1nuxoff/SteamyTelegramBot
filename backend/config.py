import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

DMARKET_API = os.getenv("DMARKET_API")
SHADOWPAY_API = os.getenv("SHADOWPAY_API")
STEAM_WEB_API = os.getenv("STEAM_WEB_API")

steam_commission_rate = 0.1233

# -------------------------------------------------------STEAM----------------------------------------------------------
STEAM_BASE_URL = "https://steamcommunity.com/market/listings"
ITEM_ORDERS_HISTOGRAM_URL = "https://steamcommunity.com/market/itemordershistogram"
STEAM_PRICE_OVERVIEW_URL = "https://steamcommunity.com/market/priceoverview/"
STEAM_MARKET_LISTINGS_URL = "https://steamcommunity.com/market/listings/"

# -------------------------------------------------------DMARKET--------------------------------------------------------
DMARKET_MARKET_ITEMS_URL = "https://api.dmarket.com/exchange/v1/market/items"

# -------------------------------------------------------SKINPORT-------------------------------------------------------

# SKINPORT_MARKET_ITEMS_URL = "https://api.skinport.com/v1/sales/history"
SKINPORT_MARKET_ITEMS_URL = "https://api.skinport.com/v1/items"

# -------------------------------------------------------BITSKINS-------------------------------------------------------
BITSKINS_SEARCH_SKIN_URL = "https://api.bitskins.com/market/search/skin_name"
BITSKINS_PRICING_LIST_URL = "https://api.bitskins.com/market/pricing/list"
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

steam_commission_rate = 0.1233


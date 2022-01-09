import os

BOT_NAME = "HelloBot"
REDIS_HOST = os.getenv("REDIS_HOST","localhost")
REDIS_PORT = os.getenv("REDIS_PORT",6379)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD","")
REDIS_TICKER_DB = os.getenv("REDIS_TICKER_DB",1)
REDIS_ATR_DB = os.getenv("REDIS_ATR_DB",2)
ROOT_PATH = os.getcwd()
REDIS_YAML_PATH = os.path.join(ROOT_PATH,"config","redis_order_dbs.yaml")
DEFAULT_REDIS_DB = 0
CRYPTO_COM_BASE_API_URL = "https://api.crypto.com/v2"
DEFAULT_BOT_ID = os.getenv("DEFAULT_BOT_ID","gALFjdrbuOGOnXLlkJYI")
BASE_URL_KRYPTON_ORDER_API = "https://test.krypton.trade/v1/api"
ALL_TIMEFRAMES = ['1m','5m','15m','1h','4h','1D','7D','1M']
PROBABLITEIS_COEFFICIENT = {"1m":0.4,"5m":0.2,"15m":0.1,"1h":0.1,"4h":0.1,"1D":0.1}
TRADING_VOLUME_COEFFICIENT = {"1m":1,"5m":1.2,"15m":1.5,"1h":2,"4h":4,"1D":8}
FIX_IRT_TRADING_AMOUNT = 200000000
FIX_USDT_TRADING_AMOUNT = 1000
MINIMUM_ORDER_IN_ORDER_BOOK = 30
REDIS_ALL_ORDERS_DB_NUMBER = os.getenv("REDIS_ALL_ORDERS_DB_NUMBER",3)

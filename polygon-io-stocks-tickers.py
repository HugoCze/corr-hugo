import os
from dotenv import load_dotenv
from polygon import RESTClient

load_dotenv()

polygon_io_api_key = os.getenv('POLYGON_IO_API_KEY')

client = RESTClient(api_key=polygon_io_api_key)

tickers = []
for t in client.list_tickers(market="stocks", type="CS", active=True, limit=1000):
    tickers.append(t)
print(tickers)
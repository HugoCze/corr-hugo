import os
from dotenv import load_dotenv
from polygon import RESTClient

load_dotenv()

polygon_io_api_key = os.getenv('POLYGON_IO_API_KEY')

client = RESTClient(api_key=polygon_io_api_key)


ticker = " * "

# List Aggregates (Bars)
aggs = []
for a in client.list_aggs(ticker=ticker, multiplier=1, timespan="minute", from_="2024-11-20", to="2024-11-21", limit=50000):
    aggs.append(a)

print(aggs)


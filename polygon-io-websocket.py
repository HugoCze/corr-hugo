
import os
from typing import List
from dotenv import load_dotenv
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage


load_dotenv()


polygon_io_api_key = os.getenv('POLYGON_IO_API_KEY')

ws = WebSocketClient(api_key=polygon_io_api_key, subscriptions=["T.AAPL"])


def handle_msg(msg: List[WebSocketMessage]):
    for m in msg:
        print(m)

ws.run(handle_msg=handle_msg)
import asyncio
import threading
import Logger


# Thread for websocket
class WebSocketThread(threading.Thread):

    stock = None
    market = None

    def __init__(self, thread_id, name, counter, stock, current_market):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter
        self.market = current_market
        self.stock = stock

    def run(self):
        Logger.log_info("Starting " + self.name)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.stock.get_ticker_websocket(self.market))
        loop.close()
        Logger.log_info("Exiting " + self.name)
import StockLib
import websockets
import json
import Logger
import datetime
import Threading

websocket_address = 'wss://ws-feed.gdax.com'
debug = True

last_update = 0;

### single market mode


async def subscribe_heartbeat(market):
    currency1 = market.get_currency1()
    currency2 = market.get_currency2()
    async with websockets.connect(websocket_address) as websocket:
        json_ticker_subscriber = json.dumps(
            {"type": "subscribe",
             "channels": [{"name": "heartbeat", "product_ids": [currency1 + "-" + currency2]}]
             })
        await websocket.send(json_ticker_subscriber)
        info_json = await websocket.recv()
        while True:
            heartbeat_json = await websocket.recv()
            market.set_last_update(heartbeat_json[heartbeat_json.find('"time":"')+19:-3])
            market.set_sequence(heartbeat_json[heartbeat_json.find('"sequence":')+11:-38])


class CoinbaseGDAX(StockLib.Stock):

    ticker_websocket = None
    iteration = 0
    last_answer = None



    def __init__(self):
        StockLib.Stock.__init__(self)
        self.stock_name = "COINBASE_GDAX"
        self.taker_fee = 0.0030  # custom set commission

    async def get_ticker_websocket(self, market):
        try:
            currency1 = market.get_currency1()
            currency2 = market.get_currency2()
            async with websockets.connect(websocket_address) as websocket:
                json_ticker_subscriber = json.dumps(
                    {"type": "subscribe", "product_ids": [currency1 + "-" + currency2], "channels": ["ticker"]})
                if debug:
                    print("json_ticker_subscriber --> : "+json_ticker_subscriber)
                await websocket.send(json_ticker_subscriber)
                info_json = await websocket.recv()
                if debug:
                    print("info_json <--: "+info_json)
                # receiving initial data
                temp_str = info_json[info_json.find("best_bid") + 11:]
                bid_rate = temp_str[:temp_str.find(",") - 1]
                if debug:
                    print("bid_rate: " + bid_rate)
                temp_str = info_json[info_json.find("best_ask") + 11:]
                ask_rate = temp_str[:temp_str.find(",") - 1]
                if debug:
                    print("ask_rate: " + ask_rate)

                market.set_top_bid_order_rate(bid_rate)
                market.set_top_ask_order_rate(ask_rate)

                subscribed_json = await websocket.recv()
                if debug:
                    print("subscribed_json <--: " + subscribed_json)
                while True:
                    update_json = await websocket.recv()
                    self.last_answer = update_json
                    if debug:
                        print("update_json: " + update_json)

                    first_find = update_json[update_json.find("best_bid") + 11:]
                    bid_rate = first_find[:first_find.find(",")-1]
                    if debug:
                        print("bid_rate: " + bid_rate)

                    third_find = update_json[update_json.find("best_ask") + 11:]
                    ask_rate = third_find[:third_find.find(",")-1]
                    if debug:
                        print("ask_rate: " + ask_rate)

                    third_find = update_json[update_json.find("time") + 7:]
                    timestamp = third_find[:third_find.find(",") - 1]
                    if debug:
                        print("timestamp: " + timestamp)

                    time = timestamp[timestamp.find("T") + 1:]
                    if debug:
                        print("time: " + time)

                    market.set_top_bid_order_rate(bid_rate)
                    market.set_top_ask_order_rate(ask_rate)

                    market.set_top_bid_order_timestamp(time)
                    market.set_top_ask_order_timestamp(time)
        except websockets.exceptions.ConnectionClosed as exc:
            print(self.last_answer)
            Logger.log_error(str(datetime.datetime.now())+" "+self.stock_name + " error code: " + str(exc.code) + ", reason: "
                      + str(exc.reason) + ", _cause_ : "+str(exc.__cause__))
            self.iteration = self.iteration + 1
            print("Restarting...")
            Coinbase_GDAXMarketThread = \
                Threading.WebSocketThread(self.iteration, "Thread: " + market.get_market_name() + str(self.iteration),
                                self.iteration, self, market)
            Coinbase_GDAXMarketThread.start()



    async def connect(self, market):
        currency1 = market.get_currency1()
        currency2 = market.get_currency2()
        async with websockets.connect(websocket_address) as websocket:
            self.ticker_websocket = websocket
            json_ticker_subscriber = json.dumps(
                {"type": "subscribe", "product_ids": [currency1+"-"+currency2], "channels": ["ticker"]})
            await websocket.send(json_ticker_subscriber)
            info_json = await websocket.recv()
            print(info_json)
            subscribed_json = await websocket.recv()
            print(subscribed_json)
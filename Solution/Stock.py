import threading
import asyncio
import json
import datetime
import requests
import websockets
import TelegramBot
from Market import Market
from Config import Config


class StockNames:
    QUOINE = "QUOINE"
    TheRockTrading = "TheRockTrading"


# Thread for websocket
class WebSocketThread(threading.Thread):

    stock = None
    market = None

    def __init__(self, thread_id, name, counter, stock, market):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter
        self.market = market
        self.stock = stock

    def run(self):
        print("Starting " + self.name)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.stock.get_ticker_websocket(self.market))
        loop.close()
        print("Exiting " + self.name)


def log_signal(signal):
    log_file = open(Config.LOG_PATH_MARKETS + "signals.txt", "a+")
    log_file.write(str(datetime.datetime.now())+": "+str(signal)+"\n")
    log_file.close()
    print(signal)
    TelegramBot.TB.send_message(signal)


def log_error(error_msg):
    log_file = open(Config.LOG_PATH_PROGRAM + "errors.txt", "a+")
    log_file.write(str(datetime.datetime.now()) + ": " + str(error_msg) + "\n")
    log_file.close()
    print(error_msg)
    TelegramBot.TB.send_message(error_msg)


# general parent class
class Stock:

    stock_name = ""
    market_list = []
    taker_fee = 0.0

    def __init__(self):
        self.stock_name = None
        self.market_list = []

    def add_market(self, currency1, currency2):
        new_market = Market(currency1, currency2, self.get_name(), self.get_taker_fee())
        self.market_list.append(new_market)
        return new_market

    def get_market(self, currency1, currency2):
        for market in self.market_list:
            if market.check_market(currency1, currency2):
                return market
            else:
                return None

    def get_market_list(self):
        return self.market_list

    def get_name(self):
        return self.stock_name

    def get_taker_fee(self):
        if self.get_name() == StockNames.QUOINE:
            return self.taker_fee_ETH
        else:
            return self.taker_fee

    def log_raw_data(self):
        for market in self.market_list:
            market.log_raw_data()


class Bittrex(Stock):
    websocket_address = None

    def __init__(self):
        Stock.__init__(self)
        self.stock_name = "BITTREX"
        self.taker_fee = 0.0025  # 2%

    def get_ticker(self, market):
        currency1 = market.get_currency1()
        currency2 = market.get_currency2()
        req = requests.get('https://bittrex.com/api/v1.1/public/getticker?market='+currency1+'-'+currency2)
        if req.json()['success']:
            market.set_top_ask_order_rate(1/req.json()["result"]["Bid"])
            market.set_top_bid_order_rate(1/req.json()["result"]["Ask"])
            self.get_market_data(market)
            return True
        else:
            log_error("Bittrex response:" + str(req.json()['message']))
            return False

    @staticmethod
    def get_market_data(market):
        currency1 = market.get_currency1()
        currency2 = market.get_currency2()
        req = requests.get('https://bittrex.com/api/v1.1/public/getorderbook?market=' + currency1 + '-' + currency2 +
                           '&type=both')
        if req.json()['success']:
            # todo: need investigation on what means what (definitions)
            market.set_top_ask_order_amount(req.json()["result"]["buy"][0]["Quantity"]*req.json()["result"]["buy"][0]
                                            ["Rate"])
            market.set_top_bid_order_amount(req.json()["result"]["sell"][0]["Quantity"]*req.json()["result"]["sell"][0]
                                            ["Rate"])
            return True
        else:
            log_error("Bittrex response:" + str(req.json()['message']))
            return False


class Kraken(Stock):
    # bitcoin = XXBT
    # all usual names are transformed to 4symbols by adding at front either X or Z
    websocket_address = None

    asset_pairs_alt_name = []
    asset_pairs = []
    assets = []
    # todo: this part of functionality needs continuation (started from ticket 0001)

    def __init__(self):
        Stock.__init__(self)
        self.stock_name = "KRAKEN"
        self.taker_fee = 0.0026  # custom set commission

    def init_markets(self):
        req = requests.get('https://api.kraken.com/0/public/AssetPairs')
        for entry in req.json()['result']:
            self.asset_pairs.append(entry)
        for asset_pair in self.asset_pairs:
            asset = req.json()['result'][asset_pair]['base']
            if asset not in self.assets:
                self.assets.append(asset)
            asset = req.json()['result'][asset_pair]['quote']
            if asset not in self.assets:
                self.assets.append(asset)
            alt_name = req.json()['result'][asset_pair]['altname']
            self.asset_pairs_alt_name.append(alt_name)
        # self.add_market(currency1, currency2)
        # self.assets.sort()
        # self.asset_pairs.sort()
        # self.asset_pairs_alt_name.sort()

    def print_assets(self):
        print("Kraken available markets:")
        print("Asset pairs:            "+str(self.asset_pairs))
        print("Asset alternative names:"+str(self.asset_pairs_alt_name))
        print("Assets :"+str(self.assets))

    @staticmethod
    def get_ticker(market):
        currency1 = market.get_currency1()
        currency2 = market.get_currency2()
        try:
            req = requests.get('https://api.kraken.com/0/public/Depth?pair='+currency1+currency2+'&count=1')
            if req.status_code == 200:
                req_json = req.json()
                # todo: 0001 on startup get dictionary for market trading pairs and alternative names like "XLTCZEUR"
                market.set_top_ask_order_rate(float(req_json["result"][currency1+currency2]['asks'][0][0]))
                market.set_top_bid_order_rate(float(req_json["result"][currency1+currency2]['bids'][0][0]))
                market.set_top_ask_order_amount(float(req_json["result"][currency1+currency2]['asks'][0][1]))
                market.set_top_bid_order_amount(float(req_json["result"][currency1+currency2]['bids'][0][1]))
                market.set_top_ask_order_timestamp(float(req_json["result"][currency1+currency2]['asks'][0][2]))
                market.set_top_bid_order_timestamp(float(req_json["result"][currency1+currency2]['bids'][0][2]))
                return True
            else:
                log_error("Kraken status not 200, status code: " + str(req.status_code) + ",raw: " + str(req.raw))
                return False
        except KeyError:
            log_error("Kraken KeyError exception, status code: " + str(req.status_code) + ",raw: " + str(req.json()))
            return False
        except:
            log_error("Kraken exception,status code: " + str(req.status_code) + ",raw: " + str(req.raw))
            return False


class QUOINE(Stock):
    websocket_address = None
    prod_market_id = None
    taker_fee_ETH = None                   # #### # introduced in QUOINE

    def __init__(self):
        Stock.__init__(self)
        self.stock_name = StockNames.QUOINE
        self.taker_fee = "ETH"  # 0.1% / 100
        # todo: don't forget about the business fact, that taker's fee is different for non-ETH trades
        self.taker_fee_ETH = 0.0010  # 0.1% / 100

    # todo: create dynamic setter of this attribute(from the QUOINE API)! it is very important to the production run!!!
    @staticmethod
    def get_prod_market_id():
        # currency1 = market.get_currency1()
        # currency2 = market.get_currency2()
        return 28

    def get_ticker(self, market):
        request_address = "https://api.quoine.com/products/" + str(self.get_prod_market_id()) + "/price_levels"
        response = requests.get(request_address)
        if response.status_code == 200:
            response_json = response.json()

            market.set_top_ask_order_rate(float(response_json["sell_price_levels"][00][0]))
            market.set_top_bid_order_rate(float(response_json["buy_price_levels"][00][0]))

            market.set_top_ask_order_amount(float(response_json["sell_price_levels"][00][1]))
            market.set_top_bid_order_amount(float(response_json["buy_price_levels"][00][1]))
            # self.get_market_data(market)
            return True
        else:
            log_error(str(self.get_name()) + " response code:" + str(response.status_code))
            return False


class Bitfinex(Stock):

    ticker_websocket = None

    websocket_address = 'wss://api.bitfinex.com/ws'

    def __init__(self):
        Stock.__init__(self)
        self.stock_name = "BITFINEX"
        self.min_margin = 0.0020  # custom set commission

    @staticmethod
    def get_ticker(market):
        currency1 = market.get_currency1()
        currency2 = market.get_currency2()
        try:
            req_json = requests.get(
                'https://api.bitfinex.com/v1/book/' + currency1 + currency2 + "?limit_bids=1&limit_asks=1").json()
            market.set_top_ask_order_rate(req_json["asks"][0]["price"])
            market.set_top_ask_order_amount(req_json["asks"][0]["amount"])
            market.set_top_bid_order_rate(req_json["bids"][0]["price"])
            market.set_top_bid_order_amount(req_json["bids"][0]["amount"])
            return True
        # todo: expand exception block
        except:
            log_error("Bitfinex exception:")
            return False

    async def get_ticker_websocket(self, market):
        currency1 = market.get_currency1()
        currency2 = market.get_currency2()
        async with websockets.connect(self.websocket_address) as websocket:
            json_ticker_subscriber = json.dumps(
                {"event": "subscribe", "channel": "ticker", "pair": currency1 + currency2})
            await websocket.send(json_ticker_subscriber)
            info_json = await websocket.recv()
            print(info_json)
            subscribed_json = await websocket.recv()
            print(subscribed_json)
            while True:
                update_json = await websocket.recv()
                if update_json.find("hb") == -1:
                    first_find = update_json[update_json.find(",")+1:]
                    bid_rate = first_find[:first_find.find(",")]

                    second_find = first_find[first_find.find(",")+1:]
                    bid_amount = second_find[:second_find.find(",")]

                    third_find = second_find[second_find.find(",")+1:]
                    ask_rate = third_find[:third_find.find(",")]

                    forth_find = third_find[third_find.find(",")+1:]
                    ask_amount = forth_find[:forth_find.find(",")]
                    # exception code received
                    if bid_rate == "\"code\":20051":
                        log_signal("websocket: \"code\":20051")
                        await self.connect(market)
                    market.set_top_bid_order_rate(bid_rate)
                    market.set_top_bid_order_amount(bid_amount)
                    market.set_top_ask_order_rate(ask_rate)
                    market.set_top_ask_order_amount(ask_amount)
                    # todo: timestamp isn't related to the ask or bid, but to the general update of the ticker
                    market.set_top_bid_order_timestamp(str(datetime.datetime.now().time()))
                    market.set_top_ask_order_timestamp(str(datetime.datetime.now().time()))

    async def connect(self, market):
        currency1 = market.get_currency1()
        currency2 = market.get_currency2()
        async with websockets.connect(self.websocket_address) as websocket:
            self.ticker_websocket = websocket
            json_ticker_subscriber = json.dumps(
                {"event": "subscribe", "channel": "ticker", "pair": currency1 + currency2})
            await websocket.send(json_ticker_subscriber)
            info_json = await websocket.recv()
            print(info_json)
            subscribed_json = await websocket.recv()
            print(subscribed_json)


class CoinbaseGDAX(Stock):
    debug = False
    ticker_websocket = None
    iteration = 0
    last_answer = None

    websocket_address = 'wss://ws-feed.gdax.com'

    def __init__(self):
        Stock.__init__(self)
        self.stock_name = "COINBASE_GDAX"
        self.taker_fee = 0.0030  # custom set commission

    async def get_ticker_websocket(self, market):
        try:
            currency1 = market.get_currency1()
            currency2 = market.get_currency2()
            async with websockets.connect(self.websocket_address) as websocket:
                json_ticker_subscriber = json.dumps(
                    {"type": "subscribe", "product_ids": [currency1 + "-" + currency2], "channels": ["level2"]})
                if self.debug:
                    print("json_ticker_subscriber --> : " + json_ticker_subscriber)
                await websocket.send(json_ticker_subscriber)
                while True:
                    # initial info
                    response_json = await websocket.recv()
                    if self.debug:
                        self.last_answer = response_json
                        print("info_json <--: "+response_json)
                    data = json.loads(response_json)

                    if data['type'] == "snapshot":
                        # load the snapshot of data
                        market.order_book.set_bid_book(data['bids'])
                        market.order_book.set_ask_book(data['asks'])
                        continue

                    if data['type'] == "subscriptions":
                        # shows current subscriptions
                        continue

                    if data['type'] == "l2update":
                        # todo: change logic over here
                        # update order book
                        new_bid = False
                        new_ask = False
                        for item in data['changes']:
                            if item[0] == "buy":
                                # bid
                                market.order_book.add_bid_data(float(item[1]), float(item[2]))
                                new_bid = True
                            if item[0] == "sell":
                                # ask
                                market.order_book.add_ask_data(float(item[1]), float(item[2]))
                                new_ask = True
                        if new_bid:
                            market.find_best_bid()
                        if new_ask:
                            market.find_best_ask()
                        # data['time'] = last update value
                        continue

        except websockets.exceptions.ConnectionClosed as exc:
            print(self.last_answer)
            log_error(str(datetime.datetime.now())+" "+self.stock_name + " error code: " + str(exc.code) + ", reason: "
                      + str(exc.reason) + ", _cause_ : "+str(exc.__cause__))
            self.iteration = self.iteration + 1
            print("Restarting...")
            Coinbase_GDAXMarketThread = \
                WebSocketThread(self.iteration, "Thread: " + market.get_market_name() + str(self.iteration),
                                self.iteration, self, market)
            Coinbase_GDAXMarketThread.start()

    async def connect(self, market):
        currency1 = market.get_currency1()
        currency2 = market.get_currency2()
        async with websockets.connect(self.websocket_address) as websocket:
            self.ticker_websocket = websocket
            json_ticker_subscriber = json.dumps(
                {"type": "subscribe", "product_ids": [currency1+"-"+currency2], "channels": ["ticker"]})
            await websocket.send(json_ticker_subscriber)
            info_json = await websocket.recv()
            print(info_json)
            subscribed_json = await websocket.recv()
            print(subscribed_json)


class TheRockTrading(Stock):
    websocket_address = None
    prod_market_id = None
    taker_fee_ETH = None                   # #### # introduced in QUOINE

    def __init__(self):
        Stock.__init__(self)
        self.stock_name = StockNames.TheRockTrading
        self.taker_fee = 0.0020  # 0.2% / 100
        self.taker_fee_ETH = None

# todo: create dynamic setter of this attribute(from the QUOINE API)! it is very important to the production run!!!
    def get_prod_market_id(self):
        # currency1 = market.get_currency1()
        # currency2 = market.get_currency2()
        return 28

    def get_ticker(self, market):
        # request_address = "https://api.therocktrading.com/v1/funds/" + "ETHEUR" + "/ticker"
        request_address = "https://api.therocktrading.com/v1/funds/" + str(market.get_currency1()) + str(market.get_currency2()) + "/orderbook"
        response = requests.get(request_address)
        if response.status_code == 200:
            response_json = response.json()

            market.set_top_ask_order_rate(float(response_json["asks"][000]["price"]))
            market.set_top_bid_order_rate(float(response_json["bids"][000]["price"]))

            market.set_top_ask_order_amount(float(response_json["asks"][000]["amount"]))
            market.set_top_bid_order_amount(float(response_json["bids"][000]["amount"]))
            # self.get_market_data(market)
            return True
        else:
            log_error(str(self.get_name()) + " response code:" + str(response.status_code))
            return False

import json
import datetime
import requests
import websockets
import Logger

CONST_CURRENCY_NAMES = ['ETH', 'BTC', 'LTC']


class StockNames:
    QUOINE = "QUOINE"
    TheRockTrading = "TheRockTrading"


class Market:
    currency1 = ""
    currency2 = ""

    taker_fee: float = 0.0
    raw_data_file_name = ""
    log_file = None

    top_ask_order_rate: float = 0
    top_ask_order_taker_fee: float = 0
    top_ask_order_amount = 0
    top_ask_order_timestamp = 0

    top_bid_order_rate: float = 0
    top_bid_order_taker_fee: float = 0
    top_bid_order_amount = 0
    top_bid_order_timestamp = 0

    stock_name = ""
    buy_orders = []
    sell_orders = []
    last_update = None
    sequence = 0
    sequence_dif = 0

    # todo: check the flow of this variable is it needed?
    response = "false"

    # functional:
    def __init__(self, currency1, currency2, stock_name, stock_tacker_fee):
        self.currency1 = currency1
        self.currency2 = currency2
        self.stock_name = stock_name
        self.taker_fee = stock_tacker_fee
        self.raw_data_file_name = stock_name + "_" + currency1 + "_" + currency2 + ".csv"
        self.init_log_file()

    def get_market_definition(self):
        result = "Stock: " + self.stock_name + " traiding pair: " + self.currency1 + "/" + self.currency2
        result = result + "\n    Ask: " + str(self.top_ask_order_rate) + " Bid: " + str(self.top_bid_order_rate)
        return result

    def get_market_name(self):
        return self.get_stock_name()+":"+self.get_currency1()+"/"+self.get_currency2()

    def check_market(self, currency1, currency2):
        if (self.currency1 == currency1)or(self.currency2 == currency1):
            if (self.currency1 == currency2) or (self.currency2 == currency2):
                return True
        return False

    def log_raw_data(self):
        Logger.log_market_raw_data(self)

    def init_log_file(self):
        Logger.init_market_log_file(self)

    # getters:
    def get_top_ask_order_rate(self):
        return float(self.top_ask_order_rate)

    def get_top_ask_order_taker_fee(self):
        return float(self.top_ask_order_taker_fee)

    def get_top_ask_order_amount(self):
        return self.top_ask_order_amount

    def get_top_ask_order_timestamp(self):
        return self.top_ask_order_timestamp

    def get_top_bid_order_rate(self):
        return float(self.top_bid_order_rate)

    def get_top_bid_order_taker_fee(self):
        return float(self.top_bid_order_taker_fee)

    def get_top_bid_order_timestamp(self):
        return self.top_bid_order_timestamp

    def get_top_bid_order_amount(self):
        return self.top_bid_order_amount

    def get_currency1(self):
        return self.currency1

    def get_currency2(self):
        return self.currency2

    def get_stock_name(self):
        return self.stock_name

    def get_response(self):
        return self.response

    # setters:
    def set_top_ask_order_rate(self, value):
        self.top_ask_order_rate = value
        self.top_ask_order_taker_fee = float(value) * float(self.taker_fee)

    def set_top_bid_order_rate(self, value):
        self.top_bid_order_rate = value
        self.top_bid_order_taker_fee = float(value) * float(self.taker_fee)

    def set_top_ask_order_amount(self, value):
        self.top_ask_order_amount = value

    def set_top_bid_order_amount(self, value):
        self.top_bid_order_amount = value

    def set_top_ask_order_timestamp(self, value):
        self.top_ask_order_timestamp = value

    def set_top_bid_order_timestamp(self, value):
        self.top_bid_order_timestamp = value

    def set_response(self, value):
        self.response = value

    def set_last_update(self, value):
        # todo implement datetime check to raise error if last update is too long
        self.last_update = value

    def set_sequence(self, value):
        self.sequence_dif = int(value) - int(self.sequence)
        if (self.sequence_dif > 100) and (self.sequence != 0):
            Logger.log_error(str(self.get_market_name()) + " too big sequence difference: " + str(self.sequence_dif))
        self.sequence = value


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

    def print_markets_info(self):
        for market in self.market_list:
            print(market.get_market_definition())

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
            Logger.log_error("Bittrex response:" + str(req.json()['message']))
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
            Logger.log_error("Bittrex response:" + str(req.json()['message']))
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
                Logger.log_error("Kraken status not 200, status code: " + str(req.status_code) + ",raw: " + str(req.raw))
                return False
        except KeyError:
            Logger.log_error("Kraken KeyError exception, status code: " + str(req.status_code) + ",raw: " + str(req.json()))
            return False
        except:
            Logger.log_error("Kraken exception,status code: " + str(req.status_code) + ",raw: " + str(req.raw))
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
            Logger.log_error(str(self.get_name()) + " response code:" + str(response.status_code))
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
            Logger.log_error("Bitfinex exception:")
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
                        Logger.log_signal("websocket: \"code\":20051")
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
            Logger.log_error(str(self.get_name()) + " response code:" + str(response.status_code))
            return False

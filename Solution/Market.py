from OrderBook import OrderBook
from Config import Config
import datetime
import os


class Market:

    currency1 = ""
    currency2 = ""

    taker_fee: float = 0.0
    raw_data_file_name = ""
    log_file = None

    top_ask_order_taker_fee: float = 0
    top_ask_order_timestamp = 0

    top_bid_order_taker_fee: float = 0
    top_bid_order_timestamp = 0

    stock_name = ""
    order_book = None
    last_update = None

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
        self.order_book = OrderBook()

    def get_market_name(self):
        return self.get_stock_name()+":"+self.get_currency1()+"/"+self.get_currency2()

    def check_market(self, currency1, currency2):
        if (self.currency1 == currency1)or(self.currency2 == currency1):
            if (self.currency1 == currency2) or (self.currency2 == currency2):
                return True
        return False

    def log_raw_data(self):
        # if file doesn't exist - create a folders and header

        self.log_file = open(Config.LOG_PATH_MARKETS + self.raw_data_file_name, "a+")
        self.log_file.write(str(datetime.datetime.now().time())+","
                            + str(self.get_top_ask_order_rate())+","+str(self.get_top_ask_order_amount())+","
                            + str(self.get_top_bid_order_rate())+","+str(self.get_top_bid_order_amount())+","
                            + str(self.get_top_ask_order_timestamp())+","+str(self.get_top_bid_order_timestamp())+","
                            + str(self.get_top_ask_order_taker_fee())+","+str(self.get_top_bid_order_taker_fee())+"\n")
        self.log_file.close()

    def init_log_file(self):
        if not os.path.isfile(Config.LOG_PATH_MARKETS + self.raw_data_file_name):
            self.log_file = open(Config.LOG_PATH_MARKETS + self.raw_data_file_name, "w+")
            self.log_file.write("python time, top ask rate, top ask amount, top bid rate, top bid amount, ask time, "
                                "bid time, ask taker fee, bid taker fee\n")
            self.log_file.close()

    # getters:
    def get_top_ask_order_rate(self):
        if self.order_book is None:
            return 0
        return float(self.order_book.get_best_ask_rate())

    def get_top_ask_order_taker_fee(self):
        return float(self.top_ask_order_taker_fee)

    def get_top_ask_order_amount(self):
        return float(self.order_book.get_best_ask_amount())

    def get_top_ask_order_timestamp(self):
        return self.top_ask_order_timestamp

    def get_top_bid_order_rate(self):
        return float(self.order_book.get_best_bid_rate())

    def get_top_bid_order_taker_fee(self):
        return float(self.top_bid_order_taker_fee)

    def get_top_bid_order_timestamp(self):
        return self.top_bid_order_timestamp

    def get_top_bid_order_amount(self):
        return float(self.order_book.get_best_bid_amount())

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
        self.order_book.best_ask_rate = float(value)
        # self.top_ask_order_rate = float(value)
        self.top_ask_order_taker_fee = float(value) * float(self.taker_fee)

    def set_top_bid_order_rate(self, value):
        self.order_book.best_bid_rate = float(value)
        # self.top_bid_order_rate = value
        self.top_bid_order_taker_fee = float(value) * float(self.taker_fee)

    def set_top_ask_order_amount(self, value):
        self.order_book.best_ask_amount = float(value)
        # self.top_ask_order_amount = value

    def set_top_bid_order_amount(self, value):
        self.order_book.best_bid_amount = float(value)
        #self.top_bid_order_amount = value

    def set_top_ask_order_timestamp(self, value):
        self.top_ask_order_timestamp = value

    def set_top_bid_order_timestamp(self, value):
        self.top_bid_order_timestamp = value

    def set_response(self, value):
        self.response = value

    def find_best_ask(self):
        self.order_book.find_best_ask()

    def find_best_bid(self):
        self.order_book.find_best_bid()

import TelegramBot
import datetime
import os

LOG_PATH_MARKETS = "../output/markets_log/"
LOG_PATH_PROGRAM = "../output/program_log/"
OUTPUT_PATH = "../output/"


def log_signal(signal):
    log_file = open(LOG_PATH_MARKETS + "signals.txt", "a+")
    log_file.write(str(datetime.datetime.now())+": "+str(signal)+"\n")
    log_file.close()
    print(signal)
    TelegramBot.TB.send_message(signal)


def log_error(error_msg):
    log_file = open(LOG_PATH_PROGRAM + "errors.txt", "a+")
    log_file.write(str(datetime.datetime.now()) + ": " + str(error_msg) + "\n")
    log_file.close()
    print(error_msg)
    TelegramBot.TB.send_message(error_msg)


def init_market_log_file(market):
    if not os.path.isfile(LOG_PATH_MARKETS + market.raw_data_file_name):
        market.log_file = open(LOG_PATH_MARKETS + market.raw_data_file_name, "w+")
        market.log_file.write("python time, top ask rate, top ask amount, top bid rate, top bid amount, ask time, "
                              "bid time, ask taker fee, bid taker fee\n")
        market.log_file.close()


def log_market_raw_data(market):
    market.log_file = open(LOG_PATH_MARKETS + market.raw_data_file_name, "a+")
    market.log_file.write(str(datetime.datetime.now().time())+","
                        + str(market.get_top_ask_order_rate())+","+str(market.get_top_ask_order_amount())+","
                        + str(market.get_top_bid_order_rate())+","+str(market.get_top_bid_order_amount())+","
                        + str(market.get_top_ask_order_timestamp())+","+str(market.get_top_bid_order_timestamp())+","
                        + str(market.get_top_ask_order_taker_fee())+","+str(market.get_top_bid_order_taker_fee())+"\n")
    market.log_file.close()

import TelegramBot
import datetime
import os

OUTPUT_PATH = "../output/"
LOG_PATH_MARKETS = "../output/markets_log/"
LOG_PATH_PROGRAM = "../output/program_log/"


def init_folders():
    if not os.path.isdir(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    if not os.path.isdir(LOG_PATH_MARKETS):
        os.makedirs(LOG_PATH_MARKETS)
    if not os.path.isdir(LOG_PATH_PROGRAM):
        os.makedirs(LOG_PATH_PROGRAM)


def log_info(info_msg):
    log_file = open(LOG_PATH_PROGRAM + "info.txt", "a+")
    log_file.write(str(datetime.datetime.now())+": "+str(info_msg)+"\n")
    log_file.close()
    print(info_msg)
    TelegramBot.TB.send_message(info_msg)


def log_signal(signal_msg):
    log_file = open(LOG_PATH_MARKETS + "signals.txt", "a+")
    log_file.write(str(datetime.datetime.now())+": "+str(signal_msg)+"\n")
    log_file.close()
    print(signal_msg)
    TelegramBot.TB.send_message(signal_msg)


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

#!/usr/bin/python

import Stock
import datetime
import asyncio
import threading
import winsound
#import pusher
import Telegram_bot

websocket_on = True
REST_on = True
activeStocks = []

log_path_markets = "../output/markets_log/"
log_path_program = "../output/program_log/"

very_small_positive_number = 0.0000000001


# Thread for sound
class SoundThread (threading.Thread):

    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter

    def run(self):
        print("Starting " + self.name)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(winsound.PlaySound('data\sounds\cash_register2.wav', winsound.SND_FILENAME))
        loop.close()
        print("Exiting " + self.name)


# Thread for websocket
class WebSocketThread (threading.Thread):

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
            Telegram_bot.TB.send_message("Starting " + self.name)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.stock.get_ticker_websocket(self.market))
            loop.close()
            print("Exiting " + self.name)


def print_trade_info(crypto_currency, fiat_currency, buy_stock_name, sell_stock_name, stock_buy_crypto_rate,
                     stock_sell_crypto_rate, trade_amount, trade_value, trade_profit, margin, operational_amount,
                     margin_to_amount_ratio, margin_to_coin_price_ratio):
    log_signal("\nBuy " + crypto_currency + " at " + buy_stock_name + " for " + str(stock_buy_crypto_rate) +
               " " + fiat_currency +
               "; Sell at " + sell_stock_name + " for " + str(stock_sell_crypto_rate) + " " + fiat_currency +
               "\n   Trade amount: " + str(trade_amount) + " " + crypto_currency +
               "\n   Trade value: " + str(trade_value) + " " + fiat_currency +
               "\n   Trade profit: " + str(trade_profit) + " " + fiat_currency +
               "\n   Calculations for 1 coin: \n   *  margin rate: " + str(margin) + " " + fiat_currency +
               "\n   *  operational amount: " + str(operational_amount) + " " + fiat_currency +
               "\n   *  margin/amount: " + str(margin_to_amount_ratio) + " %\n   *  margin/coin_price: " +
               str(margin_to_coin_price_ratio)+"\n")

def is_margin_between_markets(market1, market2):
    # todo: evaluate max value of the trade (order value)
    m1_top_ask_order_rate = market1.get_top_ask_order_rate()
    m1_top_ask_order_taker_fee = market1.get_top_ask_order_taker_fee()
    m1_top_bid_order_rate = market1.get_top_bid_order_rate()
    m1_top_bid_order_taker_fee = market1.get_top_bid_order_taker_fee()
    m2_top_ask_order_rate = market2.get_top_ask_order_rate()
    m2_top_ask_order_taker_fee = market2.get_top_ask_order_taker_fee()
    m2_top_bid_order_rate = market2.get_top_bid_order_rate()
    m2_top_bid_order_taker_fee = market2.get_top_bid_order_taker_fee()

    if m1_top_ask_order_rate + m1_top_ask_order_taker_fee < m2_top_bid_order_rate - m2_top_bid_order_taker_fee:
        margin = m2_top_bid_order_rate - m1_top_ask_order_rate - m2_top_bid_order_taker_fee - m1_top_ask_order_taker_fee
        operational_amount = m1_top_ask_order_rate + m1_top_ask_order_taker_fee + \
                             m2_top_bid_order_rate + m2_top_bid_order_taker_fee
        margin_to_amount_ratio = margin / (operational_amount+very_small_positive_number)
        margin_to_coin_price_ratio = margin / (m1_top_ask_order_rate+very_small_positive_number)
        m2_amount = float(market2.get_top_bid_order_amount())
        m1_amount = float(market1.get_top_ask_order_amount())
        trade_amount = min(m1_amount, m2_amount)
        trade_value = trade_amount * operational_amount
        trade_profit = trade_amount * margin
        print_trade_info(crypto_currency=market2.get_currency1(), fiat_currency=market2.get_currency2(), buy_stock_name=market1.get_stock_name(), sell_stock_name=market2.get_stock_name(),
                         stock_buy_crypto_rate=m1_top_ask_order_rate, stock_sell_crypto_rate=m2_top_bid_order_rate, trade_amount=trade_amount, trade_value=trade_value, trade_profit=trade_profit,
                         margin=margin, operational_amount=operational_amount, margin_to_amount_ratio=margin_to_amount_ratio, margin_to_coin_price_ratio=margin_to_coin_price_ratio)
        audio_thread = SoundThread(0, "sound", 0)
        audio_thread.start()
    if m2_top_ask_order_rate + m2_top_ask_order_taker_fee < m1_top_bid_order_rate - m1_top_bid_order_taker_fee:
        margin = m1_top_bid_order_rate - m2_top_ask_order_rate - m2_top_ask_order_taker_fee - m1_top_bid_order_taker_fee
        operational_amount = m2_top_ask_order_rate + m2_top_ask_order_taker_fee + \
                             m1_top_bid_order_rate + m1_top_bid_order_taker_fee
        margin_to_amount_ratio = margin/(operational_amount + very_small_positive_number)
        margin_to_coin_price_ratio = margin/(m2_top_ask_order_rate + very_small_positive_number)
        m2_amount = float(market2.get_top_ask_order_amount())
        m1_amount = float(market1.get_top_bid_order_amount())
        trade_amount = min(m1_amount, m2_amount)
        trade_value = trade_amount * operational_amount
        trade_profit = trade_amount * margin
        print_trade_info(crypto_currency=market1.get_currency1(), fiat_currency=market1.get_currency2(), buy_stock_name=market2.get_stock_name(), sell_stock_name=market1.get_stock_name(),
                         stock_buy_crypto_rate=m2_top_ask_order_rate, stock_sell_crypto_rate=m1_top_bid_order_rate, trade_amount=trade_amount, trade_value=trade_value, trade_profit=trade_profit,
                         margin=margin, operational_amount=operational_amount, margin_to_amount_ratio=margin_to_amount_ratio, margin_to_coin_price_ratio=margin_to_coin_price_ratio)
        audio_thread = SoundThread(0, "sound", 0)
        audio_thread.start()
    return


def log_signal(signal):
    log_file = open(log_path_markets+"signals.txt", "a")
    log_file.write(str(datetime.datetime.now())+": "+str(signal)+"\n")
    log_file.close()
    print(str(datetime.datetime.now())+": "+str(signal))
    Telegram_bot.TB.send_message(signal)


def gather_info(iterator, active_stocks):
    # print(str(iterator)+". " + str(datetime.datetime.now().time()))
    group_response = True
    # todo: move to the separate threads
    # REST only
    for stock in active_stocks:
        if stock.websocket_address is None:
            for market in stock.get_market_list():
                market.set_response(stock.get_ticker(market))
    # All
    for stock in active_stocks:
        stock.log_raw_data()
        # stock.print_markets_info()
    # REST only
    for stock in active_stocks:
        if stock.websocket_address is None:
            for market in stock.get_market_list():
                if not market.get_response():
                    group_response = False
    if group_response:
        return True
    else:
        return True


# main here

# Bitfinex init:

# Bitfinex = Stock.Bitfinex()
# Bitfinex_BTC_EUR_market = Bitfinex.add_market("BTC", "EUR")
# Bitfinex_ETH_EUR_market = Bitfinex.add_market("ETH", "EUR")
# Bitfinex_EOS_EUR_market = Bitfinex.add_market("EOS", "EUR")
# Bitfinex_BCH_EUR_market = Bitfinex.add_market("BCH", "EUR") pair doesn't exist on Bitfinex

# initialisation of Bitfinex websocket threads
# threadIterator = 0
# for market in Bitfinex.get_market_list():
#    threadIterator = threadIterator + 1
#    BitfinexMarketThread = \
#        WebSocketThread(threadIterator, "Thread: " + market.get_market_name(), threadIterator, Bitfinex, market)
#    BitfinexMarketThread.start()

# COINBASE_GDAX init:

Coinbase_GDAX = Stock.CoinbaseGDAX()
# Coinbase_GDAX_ETH_EUR_market = Coinbase_GDAX.add_market("ETH", "EUR")
Coinbase_GDAX_BTC_USD_market = Coinbase_GDAX.add_market("BTC", "USD")

# initialisation of Coinbase_X websocket threads

if websocket_on:
    threadIterator = 0
    for market in Coinbase_GDAX.get_market_list():
        threadIterator = threadIterator + 1
        Coinbase_GDAXMarketThread = \
            WebSocketThread(threadIterator, "Thread: " + market.get_market_name(), threadIterator, Coinbase_GDAX, market)
        Coinbase_GDAXMarketThread.start()

# Bittrex init:
# Bittrex = Stock.Bittrex()
# Bittrex_BTC_USDT_market = Bittrex.add_market("BTC", "TUSD")

# Kraken init:
Kraken = Stock.Kraken()
# Kraken_BTC_EUR_market = Kraken.add_market("XXBT", "ZEUR")
Kraken_BTC_USD_market = Kraken.add_market("XXBT", "ZUSD")
# Kraken_ETH_EUR_market = Kraken.add_market("XETH", "ZEUR")
# Kraken_EOS_EUR_market = Kraken.add_market("EOS", "EUR")
# Kraken_BCH_EUR_market = Kraken.add_market("BCH", "EUR") pair doesn't exist on Bitfinex

# QUOINE init:
# QUOINE = Stock.QUOINE()
# QUOINE_ETH_EUR_market = QUOINE.add_market("ETH", "EUR")     # ####### #currency names may be different

# TheRockTrading init:
# TheRockTrading = Stock.TheRockTrading()
# TheRockTrading_ETH_EUR_market = TheRockTrading.add_market("ETH", "EUR")
# TheRockTrading_BTC_EUR_market = TheRockTrading.add_market("BTC", "EUR")

# activeStocks.append(Bittrex)
# activeStocks.append(QUOINE)
activeStocks.append(Kraken)
# activeStocks.append(TheRockTrading)
activeStocks.append(Coinbase_GDAX)

# implementation of check
last_check = datetime.datetime.now()
iteration = datetime.timedelta(seconds=1)
i = 0

# todo: must be reworked into threads
while REST_on:
    if datetime.datetime.now() - iteration > last_check:
        i = i+1
        response = gather_info(i, activeStocks)
        last_check = datetime.datetime.now()
        is_margin_between_markets(Kraken_BTC_USD_market, Coinbase_GDAX_BTC_USD_market)
        if not response:
            last_check = last_check + datetime.timedelta(minutes=1)
            log_signal("No response waiting until: " + str(last_check))

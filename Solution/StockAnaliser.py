#!/usr/bin/python

import datetime
import Logger
import Threading
import StockLib
import CoinbaseAPI

WEBSOCKET_ON = True
REST_ON = False
VERY_SMALL_POSITIVE_NUMBER = 0.0000000001


activeStocks = []


def print_trade_info(crypto_currency, fiat_currency, buy_stock_name, sell_stock_name, stock_buy_crypto_rate,
                     stock_sell_crypto_rate, trade_amount, trade_value, trade_profit, margin, operational_amount,
                     margin_to_amount_ratio, margin_to_coin_price_ratio):
    Logger.log_signal("\nBuy " + crypto_currency + " at " + buy_stock_name + " for " + str(stock_buy_crypto_rate) +
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
        margin_to_amount_ratio = margin / (operational_amount + VERY_SMALL_POSITIVE_NUMBER)
        margin_to_coin_price_ratio = margin / (m1_top_ask_order_rate + VERY_SMALL_POSITIVE_NUMBER)
        m2_amount = float(market2.get_top_bid_order_amount())
        m1_amount = float(market1.get_top_ask_order_amount())
        trade_amount = min(m1_amount, m2_amount)
        trade_value = trade_amount * operational_amount
        trade_profit = trade_amount * margin
        print_trade_info(crypto_currency=market2.get_currency1(), fiat_currency=market2.get_currency2(), buy_stock_name=market1.get_stock_name(), sell_stock_name=market2.get_stock_name(),
                         stock_buy_crypto_rate=m1_top_ask_order_rate, stock_sell_crypto_rate=m2_top_bid_order_rate, trade_amount=trade_amount, trade_value=trade_value, trade_profit=trade_profit,
                         margin=margin, operational_amount=operational_amount, margin_to_amount_ratio=margin_to_amount_ratio, margin_to_coin_price_ratio=margin_to_coin_price_ratio)
    if m2_top_ask_order_rate + m2_top_ask_order_taker_fee < m1_top_bid_order_rate - m1_top_bid_order_taker_fee:
        margin = m1_top_bid_order_rate - m2_top_ask_order_rate - m2_top_ask_order_taker_fee - m1_top_bid_order_taker_fee
        operational_amount = m2_top_ask_order_rate + m2_top_ask_order_taker_fee + \
                             m1_top_bid_order_rate + m1_top_bid_order_taker_fee
        margin_to_amount_ratio = margin/(operational_amount + VERY_SMALL_POSITIVE_NUMBER)
        margin_to_coin_price_ratio = margin/(m2_top_ask_order_rate + VERY_SMALL_POSITIVE_NUMBER)
        m2_amount = float(market2.get_top_ask_order_amount())
        m1_amount = float(market1.get_top_bid_order_amount())
        trade_amount = min(m1_amount, m2_amount)
        trade_value = trade_amount * operational_amount
        trade_profit = trade_amount * margin
        print_trade_info(crypto_currency=market1.get_currency1(), fiat_currency=market1.get_currency2(), buy_stock_name=market2.get_stock_name(), sell_stock_name=market1.get_stock_name(),
                         stock_buy_crypto_rate=m2_top_ask_order_rate, stock_sell_crypto_rate=m1_top_bid_order_rate, trade_amount=trade_amount, trade_value=trade_value, trade_profit=trade_profit,
                         margin=margin, operational_amount=operational_amount, margin_to_amount_ratio=margin_to_amount_ratio, margin_to_coin_price_ratio=margin_to_coin_price_ratio)


def gather_info(active_stocks):
    group_response = True
    # todo: move to the separate threads
    # todo: check wtf is going on with group_response
    # REST only
    for stock in active_stocks:
        if stock.websocket_address is None:
            for currentMarket in stock.get_market_list():
                currentMarket.set_response(stock.get_ticker(currentMarket))
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


Logger.init_folders()

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

Coinbase_GDAX = CoinbaseAPI.CoinbaseGDAX()
# Coinbase_GDAX_ETH_EUR_market = Coinbase_GDAX.add_market("ETH", "EUR")
# Coinbase_GDAX_BTC_USD_market = Coinbase_GDAX.add_market("BTC", "USD")
Coinbase_GDAX_BTC_EUR_market = Coinbase_GDAX.add_market("BTC", "EUR")

# initialisation of Coinbase_X websocket threads

if WEBSOCKET_ON:
    threadIterator = 0
    for market in Coinbase_GDAX.get_market_list():
        threadIterator = threadIterator + 1
        Coinbase_GDAXMarketThread = \
            Threading.WebSocketThread(threadIterator, "Thread: " + market.get_market_name(), threadIterator,
                                      Coinbase_GDAX, market)
        Coinbase_GDAXMarketThread.start()

# Bittrex init:
# Bittrex = Stock.Bittrex()
# Bittrex_BTC_USDT_market = Bittrex.add_market("BTC", "TUSD")

# Kraken init:
Kraken = StockLib.Kraken()
Kraken_BTC_EUR_market = Kraken.add_market("XXBT", "ZEUR")
# Kraken_BTC_USD_market = Kraken.add_market("XXBT", "ZEUR")
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
while REST_ON:
    if datetime.datetime.now() - iteration > last_check:
        response = gather_info(activeStocks)
        last_check = datetime.datetime.now()
        is_margin_between_markets(Kraken_BTC_EUR_market, Coinbase_GDAX_BTC_EUR_market)
        if not response:
            last_check = last_check + datetime.timedelta(minutes=1)
            Logger.log_signal("No response waiting until: " + str(last_check))

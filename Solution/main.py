import CoinbaseAPI
import Threading
import datetime


def coinbase_init(currency1, currency2):
    coinbase_gdax = CoinbaseAPI.CoinbaseGDAX()
    coinbase_gdax_btc_eur_market = coinbase_gdax.add_market(currency1, currency2)
    thread_iterator = 0
    coinbase_btc_eur_heartbeat_thread = \
        Threading.WebSocketThread(thread_iterator, "Thread: coinbase heartbeat",
                                  thread_iterator, coinbase_gdax, coinbase_gdax_btc_eur_market,
                                  CoinbaseAPI.subscribe_heartbeat)
    coinbase_btc_eur_heartbeat_thread.start()


coinbase_init("BTC", "EUR")



# Class that represents Order Book structure
class OrderBook:
    ask_book = {}
    bid_book = {}

    def __init__(self, ask_book, bid_book):
        self.rewrite(ask_book, bid_book)
        print("init")

    def rewrite(self, ask_book, bid_book):
        self.ask_book = ask_book
        self.bid_book = bid_book


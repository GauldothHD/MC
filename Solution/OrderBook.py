# we hold top values on top and sort every update


class OrderBook:

    debug = True

    bid_book = [[float, float]]
    best_bid_rate = None
    best_bid_amount = 0

    ask_book = [[float, float]]
    best_ask_rate = None
    best_ask_amount = 0

    def set_bid_book(self, bb):
        self.bid_book = bb
        self.find_best_bid()
        return True

    def set_ask_book(self, ab):
        self.ask_book = ab
        self.find_best_ask()
        return True

    def get_best_bid_rate(self):
        if self.best_bid_rate is None:
            return False
        return float(self.best_bid_rate)

    def get_best_ask_rate(self):
        if self.best_ask_rate is None:
            return False
        return float(self.best_ask_rate)

    def get_best_bid_amount(self):
        return self.best_bid_amount

    def get_best_ask_amount(self):
        return self.best_ask_amount

    def find_best_bid(self):
        if self.best_bid_rate is None:
            self.best_bid_rate = float(self.bid_book[0][0])
            self.best_bid_amount = float(self.bid_book[0][1])
        for item in self.bid_book:
            if float(item[0]) > self.best_bid_rate:
                self.best_bid_rate = float(item[0])
                self.best_bid_amount = float(item[1])

    def find_best_ask(self):
        if self.best_ask_rate is None:
            self.best_ask_rate = float(self.ask_book[0][0])
            self.best_ask_amount = float(self.ask_book[0][1])
        for item in self.ask_book:
            if float(item[0]) < self.best_ask_rate:
                self.best_ask_rate = float(item[0])
                self.best_ask_amount = float(item[1])

    def add_bid_data(self, rate, amount):
        if type(rate) is not float:
            raise TypeError("ONLY FLOAT rates")
        if type(amount) is not float:
            raise TypeError("ONLY FLOAT amounts")
        ii = 0
        for item in self.bid_book:
            if item[0] == float(rate):
                if amount == 0:
                    # removed
                    self.bid_book = self.bid_book[:ii]+self.bid_book[ii+1:]
                    self.best_bid_rate = 0
                    self.best_bid_amount = 0
                    return True
                else:
                    # changed
                    self.bid_book[ii][1] = float(amount)
                    return True
            ii = ii+1
        # new
        self.bid_book.append([float(rate), float(amount)])
        return False

    def add_ask_data(self, rate, amount):
        if type(rate) is not float:
            raise TypeError("ONLY FLOAT rates")
        if type(amount) is not float:
            raise TypeError("ONLY FLOAT amounts")
        ii = 0
        for item in self.ask_book:
            if item[0] == float(rate):
                if amount == 0:
                    # removed
                    self.ask_book = self.ask_book[:ii]+self.ask_book[ii+1:]
                    self.best_ask_rate = 999999999
                    self.best_ask_amount = 0
                    return True
                else:
                    # changed
                    self.ask_book[ii][1] = float(amount)
                    return True
            ii = ii+1
        # new
        self.ask_book.append([float(rate), float(amount)])
        return False
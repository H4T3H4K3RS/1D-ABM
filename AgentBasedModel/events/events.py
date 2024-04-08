from AgentBasedModel.simulator import Simulator
from AgentBasedModel.agents import Trader, Universalist, Fundamentalist, MarketMaker
from AgentBasedModel.utils import logging
from AgentBasedModel.utils.orders import Order
from itertools import chain

colors = [
    (31, 119, 180),  # blue
    (255, 127, 14),  # orange
    (44, 160, 44),  # green
    (214, 39, 40),  # red
    (148, 103, 189),  # purple
    (140, 86, 75),  # brown
    (227, 119, 194),  # pink
    (127, 127, 127),  # gray
    (188, 189, 34),  # yellow-green
    (23, 190, 207),  # cyan
]

colors = [(r / 255.0, g / 255.0, b / 255.0) for r, g, b in colors]


class Event:
    def __init__(self, it: int):
        self.it = it  # Activation it
        self.simulator = None
        self.color = colors[0]

    def __repr__(self):
        return f'empty (it={self.it})'

    def call(self, it: int):
        if self.simulator is None:
            raise Exception('No simulator link found')
        if it != self.it:
            return True
        return False

    def link(self, simulator: Simulator):
        self.simulator = simulator
        return self

    def to_dict(self) -> dict:
        return {
            'it': self.it,
            'type': self.__class__.__name__,
        }


class FundamentalPriceShock(Event):
    def __init__(self, it: int, price_change: float):
        super().__init__(it)
        self.color = colors[1]
        self.dp = price_change

    def __repr__(self):
        return f'fundamental price shock (it={self.it}, dp={self.dp})'

    def call(self, it: int):
        if super().call(it):
            return
        divs = self.simulator.exchange.dividend_book  # link to dividend book
        r = self.simulator.exchange.risk_free  # risk-free rate

        self.simulator.exchange.dividend_book = [div + self.dp * r for div in divs]


class MarketPriceShock(Event):
    def __init__(self, it: int, price_change: float):
        super().__init__(it)
        self.color = colors[2]
        self.dp = round(price_change)

    def __repr__(self):
        return f'market price shock (it={self.it}, dp={self.dp})'

    def call(self, it: int):
        if super().call(it):
            return

        book = self.simulator.exchange.order_book
        for order in chain(*book.values()):
            order.price += round(self.dp, 1)


class LiquidityShock(Event):
    def __init__(self, it: int, volume_change: float):
        super().__init__(it)
        self.color = colors[3]
        self.dv = round(volume_change)

    def __repr__(self):
        return f'liquidity shock (it={self.it}, dv={self.dv})'

    def call(self, it: int):
        if super().call(it):
            return
        exchange = self.simulator.exchange
        pseudo_trader = Trader(exchange, 1e6, int(1e4))
        if self.dv < 0:  # buy
            order = Order(exchange.order_book['ask'].last.price, abs(self.dv), 'bid', it, pseudo_trader)
        else:  # sell
            order = Order(exchange.order_book['bid'].last.price, abs(self.dv), 'ask', it, pseudo_trader)
        exchange.market_order(order)


class InformationShock(Event):
    def __init__(self, it, access: int):
        super().__init__(it)
        self.color = colors[4]
        self.access = access

    def __repr__(self):
        return f'information shock (it={self.it}, access={self.access})'

    def call(self, it: int):
        if super().call(it):
            return
        for trader in self.simulator.traders:
            if type(trader) in (Universalist, Fundamentalist):
                trader.access = self.access


class MarketMakerIn(Event):
    def __init__(self, it, cash: float = 10 ** 3, assets: int = 0, softlimit: int = 100):
        super().__init__(it)
        self.color = colors[5]
        self.cash = cash
        self.assets = assets
        self.softlimit = softlimit

    def __repr__(self):
        return f'mm in (it={self.it}, softlimit={self.softlimit})'

    def call(self, it: int):
        if super().call(it):
            return

        maker = MarketMaker(self.simulator.exchange, self.cash, self.assets, self.softlimit)
        self.simulator.traders.append(maker)


class MarketMakerOut(Event):
    def __init__(self, it):
        super().__init__(it)
        self.color = colors[6]

    def __repr__(self):
        return f'mm out (it={self.it})'

    def call(self, it: int):
        if super().call(it):
            return

        self.simulator.traders = [tr for tr in self.simulator.traders if type(tr) != MarketMaker]


class TransactionCost(Event):
    def __init__(self, it, cost):
        super().__init__(it)
        self.color = colors[7]
        self.cost = cost

    def __repr__(self):
        return f'transaction cost (it={self.it}, cost={self.cost}%)'

    def call(self, it: int):
        if super().call(it):
            return

        self.simulator.exchange.transaction_cost = self.cost


class SignalThreshold(Event):
    def __init__(self, it, signal_threshold, traders: list = None):
        super().__init__(it)
        self.color = colors[8]
        self.signal_threshold = signal_threshold
        self.traders = traders

    def __repr__(self):
        traders = ','.join(list(map(lambda x: x, self.traders))) if self.traders is not None else 'ALL'
        return f'signal threshold (it={self.it}, threshold={self.signal_threshold}, traders={traders})'

    def call(self, it: int):
        if super().call(it):
            return

        for trader in self.simulator.traders:
            if self.traders is None or trader.__class__.__name__ in self.traders:
                trader.signal_threshold = self.signal_threshold

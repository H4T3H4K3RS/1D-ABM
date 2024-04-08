from AgentBasedModel.simulator import SimulatorInfo
import AgentBasedModel.utils.math as math
import matplotlib.pyplot as plt

from AgentBasedModel.utils import logging


def plot_price(info: SimulatorInfo, ax: plt.Axes = None, spread=False, rolling: int = 1, figsize=(6, 6),
               save_path: str = None):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    ax.set_title(f'Stock Price {info.exchange.id}') if rolling == 1 else plt.title(
        f'Stock Price {info.exchange.id} (MA {rolling})')
    ax.set_xlabel('Iterations')
    ax.set_ylabel('Price')
    ax.plot(range(rolling - 1, len(info.prices)), math.rolling(info.prices, rolling), color='black')
    if spread:
        v1 = [el['bid'] for el in info.spreads]
        v2 = [el['ask'] for el in info.spreads]
        ax.plot(range(rolling - 1, len(v1)), math.rolling(v1, rolling), label='bid', color='green')
        ax.plot(range(rolling - 1, len(v2)), math.rolling(v2, rolling), label='ask', color='red')
    for event in info.events:
        ax.axvline(x=event.it, color=event.color, linestyle='--', label=event.__repr__())
    ax.legend()
    # plt.show()
    if save_path is not None:
        plt.savefig(save_path)
    return ax


def plot_price_fundamental(info: SimulatorInfo, ax: plt.Axes = None, spread=False, access: int = 1, rolling: int = 1,
                           figsize=(6, 6), save_path: str = None):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    if rolling == 1:
        ax.set_title(f'Stock {info.exchange.id} Fundamental and Market value')
    else:
        ax.set_title(f'Stock {info.exchange.id} Fundamental and Market value (MA {rolling})')
    ax.set_xlabel('Iterations')
    ax.set_ylabel('Present value')
    if spread:
        v1 = [el['bid'] for el in info.spreads]
        v2 = [el['ask'] for el in info.spreads]
        ax.plot(range(rolling - 1, len(v1)), math.rolling(v1, rolling), label='bid', color='green')
        ax.plot(range(rolling - 1, len(v2)), math.rolling(v2, rolling), label='ask', color='red')
    ax.plot(range(rolling - 1, len(info.prices)), math.rolling(info.prices, rolling), label='market value',
            color='black')
    ax.plot(range(rolling - 1, len(info.prices)), math.rolling(info.fundamental_value(access), rolling),
            label='fundamental value')
    for event in info.events:
        ax.axvline(x=event.it, color=event.color, linestyle='--', label=event.__repr__())
    ax.legend()
    # plt.show()
    if save_path is not None:
        plt.savefig(save_path)
    return ax


def plot_arbitrage(info: SimulatorInfo, ax: plt.Axes = None, access: int = 1, rolling: int = 1, figsize=(6, 6),
                   save_path: str = None):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    if rolling == 1:
        ax.set_title(f'Stock {info.exchange.id} Fundamental and Market value difference %')
    else:
        ax.set_title(f'Stock {info.exchange.id} Fundamental and Market value difference % (MA {rolling})')
    ax.set_xlabel('Iterations')
    ax.set_ylabel('Present value')
    market = info.prices
    fundamental = info.fundamental_value(access)
    arbitrage = [(fundamental[i] - market[i]) / fundamental[i] for i in range(len(market))]
    ax.plot(range(rolling, len(arbitrage) + 1), math.rolling(arbitrage, rolling), color='black')
    for event in info.events:
        ax.axvline(x=event.it, color=event.color, linestyle='--', label=event.__repr__())
    ax.legend()
    # plt.show()
    if save_path is not None:
        plt.savefig(save_path)
    return ax


def plot_dividend(info: SimulatorInfo, ax: plt.Axes = None, rolling: int = 1, figsize=(6, 6), save_path: str = None):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    ax.set_title(f'Stock {info.exchange.id} Dividend') if rolling == 1 else plt.title(
        f'Stock {info.exchange.id} Dividend (MA {rolling})')
    ax.set_xlabel('Iterations')
    ax.set_ylabel('Dividend')
    ax.plot(range(rolling, len(info.dividends) + 1), math.rolling(info.dividends, rolling), color='black')
    for event in info.events:
        ax.axvline(x=event.it, color=event.color, linestyle='--', label=event.__repr__())
    ax.legend()
    # plt.show()
    if save_path is not None:
        plt.savefig(save_path)
    return ax


def plot_orders(info: SimulatorInfo, ax: plt.Axes = None, stat: str = 'quantity', rolling: int = 1, figsize=(6, 6),
                save_path: str = None):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    ax.set_title(f'Book {info.exchange.id} Orders') if rolling == 1 else plt.title(
        f'Book {info.exchange.id} Orders (MA {rolling})')
    ax.set_xlabel('Iterations')
    ax.set_ylabel(stat)
    v1 = [v[stat]['bid'] for v in info.orders]
    v2 = [v[stat]['ask'] for v in info.orders]
    ax.plot(range(rolling, len(v1) + 1), math.rolling(v1, rolling), label='bid', color='green')
    ax.plot(range(rolling, len(v2) + 1), math.rolling(v2, rolling), label='ask', color='red')
    for event in info.events:
        ax.axvline(x=event.it, color=event.color, linestyle='--', label=event.__repr__())
    ax.legend()
    # plt.show()
    if save_path is not None:
        plt.savefig(save_path)
    return ax


def plot_volatility_price(info: SimulatorInfo, ax: plt.Axes = None, window: int = 5, figsize=(6, 6),
                          save_path: str = None):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    ax.set_title(f'Stock {info.exchange.id} Price Volatility (window {window})')
    ax.set_xlabel('Iterations')
    ax.set_ylabel('Price Volatility')
    volatility = info.price_volatility(window)
    ax.plot(range(window, len(volatility) + window), volatility, color='black')
    for event in info.events:
        ax.axvline(x=event.it, color=event.color, linestyle='--', label=event.__repr__())
    ax.legend()
    # plt.show()
    if save_path is not None:
        plt.savefig(save_path)
    return ax


def plot_volatility_return(info: SimulatorInfo, ax: plt.Axes = None, window: int = 5, figsize=(6, 6),
                           save_path: str = None):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    ax.set_title(f'Stock {info.exchange.id} Return Volatility (window {window})')
    ax.set_xlabel('Iterations')
    ax.set_ylabel('Return Volatility')
    volatility = info.return_volatility(window)
    ax.plot(range(window, len(volatility) + window), volatility, color='black')
    for event in info.events:
        ax.axvline(x=event.it, color=event.color, linestyle='--', label=event.__repr__())
    ax.legend()
    # plt.show()
    if save_path is not None:
        plt.savefig(save_path)
    return ax


def plot_liquidity(info: SimulatorInfo, ax: plt.Axes = None, rolling: int = 1, figsize=(6, 6), save_path: str = None):
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    ax.set_title(f'Liquidity {info.exchange.id}') if rolling == 1 else plt.title(
        f'Liquidity {info.exchange.id} (MA {rolling})')
    ax.set_xlabel('Iterations')
    ax.set_ylabel('Spread / avg. Price')
    ax.plot(info.liquidity(rolling), color='black')
    for event in info.events:
        ax.axvline(x=event.it, color=event.color, linestyle='--', label=event.__repr__())
    ax.legend()
    # plt.show()
    if save_path is not None:
        plt.savefig(save_path)
    return ax

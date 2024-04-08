import json
import os

import AgentBasedModel
from AgentBasedModel import *
from AgentBasedModel.utils import logging
from AgentBasedModel.utils.math import *

import itertools
from tqdm import tqdm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

RANGE = list(range(3, 6))
WINDOW = 5
SIZE = 10
FUNCS = [
    ('price', lambda info, w: info.prices)
]

needed_paths = [
    "output/plots/dashboards",
    "output/logs",
    "output/scenarios",
]
for path in needed_paths:
    if not os.path.exists(path):
        os.makedirs(path)

traders = list()
before = list()
after = list()
with open("config.json", "r", encoding="utf-8") as f:
    config = json.loads(f.read())
logging.Logger.info(f"Config: {json.dumps(config)}")

configs = AgentBasedModel.utils.generate_configs(iterations=1000)
with open(f"output/scenarios.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(configs))
for scenario, scenario_configs in configs.items():
    AgentBasedModel.utils.logging.Logger.error(f"Scenario: {scenario}. Configs: [{len(scenario_configs)}]")
    events_dfs = []
    for config_i, config in enumerate(scenario_configs):
        AgentBasedModel.ExchangeAgent.id = 0
        AgentBasedModel.Trader.id = 0
        AgentBasedModel.utils.logging.Logger.error(f"Config: #{config_i}")
        AgentBasedModel.utils.logging.Logger.error(f"Events: {config['events']}")
        traders = []
        events = []
        exchange = AgentBasedModel.ExchangeAgent(**config["exchange"])
        for trader in config["traders"]:
            params = dict(**trader)
            params["market"] = exchange
            params.pop("type")
            params.pop("count")
            traders.extend(
                [
                    getattr(AgentBasedModel.agents, trader["type"])(**params) for _ in range(trader["count"])
                ]
            )
        for event in config["events"]:
            params = dict(**event)
            params.pop("type")
            events.append(
                getattr(AgentBasedModel.events, event["type"])(**params)
            )
        simulator = AgentBasedModel.Simulator(**{
            'exchange': exchange,
            'traders': traders,
            'events': events,
        })
        simulator.simulate(config["iterations"])
        infos = [simulator.info]

        for _ in range(len(infos)):
            # info_dict = infos[_].to_dict(config)
            # with open(f"output/info/json/{config_i}_{_}.json", "w", encoding="utf-8") as f:
            #     f.write(json.dumps(info_dict))
            # df = AgentBasedModel.utils.export.make_df(info=info_dict, config=config)
            # df.to_csv(f"output/info/csv/{config_i}_{_}.csv", index=False)
            events_dfs.append(AgentBasedModel.utils.make_event_df(info=infos[_], config=config))
            plot_price(infos[_], save_path=f"output/plots/{config_i}_price_{_}.png")
            plot_price_fundamental(infos[_], save_path=f"output/plots/{config_i}_price_fundamental_{_}.png")
            plot_arbitrage(infos[_], save_path=f"output/plots/{config_i}_arbitrage_{_}.png")
            plot_dividend(infos[_], save_path=f"output/plots/{config_i}_dividend_{_}.png")
            plot_orders(infos[_], save_path=f"output/plots/{config_i}_orders_{_}.png")
            plot_volatility_price(infos[_], save_path=f"output/plots/{config_i}_volatility_price_{_}.png")
            plot_volatility_return(infos[_], save_path=f"output/plots/{config_i}_volatility_return_{_}.png")
            plot_liquidity(infos[_], save_path=f"output/plots/{config_i}_liquidity_{_}.png")

            fig, axs = plt.subplots(8, 1, figsize=(15, 25))
            counters = ""
            for trader in config["traders"]:
                counters += f"{trader['type']}: {trader['count']}\n"
            fig.suptitle(f"Dashboard {config_i}.\n{counters}\n")
            plot_price_fundamental(infos[_], ax=axs[0])
            plot_arbitrage(infos[_], ax=axs[1])
            plot_price(infos[_], ax=axs[2])
            plot_dividend(infos[_], ax=axs[3])
            plot_orders(infos[_], ax=axs[4])
            plot_volatility_price(infos[_], ax=axs[5])
            plot_volatility_return(infos[_], ax=axs[6])
            plot_liquidity(infos[_], ax=axs[7])

            plt.tight_layout()
            plt.savefig(f"output/plots/dashboards/{config_i}.png")
    events_dfs = pd.concat(events_dfs)
    events_dfs.to_csv(f"output/scenarios/{scenario}.csv", index=False)

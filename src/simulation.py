from dataclasses import dataclass
from enum import Enum

import numpy as np

from src.config import SimulationConfig
from src.environment import MarketEnvironment
from src.market_maker import AvellanedaStoikov, NaiveMarketMaker


class Strategy(Enum):
    NAIVE = "naive"
    AVELLANEDA_STOIKOV = "avellaneda_stoikov"


@dataclass
class TradeLogEntry:
    time: float
    mid_price: float
    bid: float
    ask: float
    bid_filled: bool
    ask_filled: bool
    inventory: int
    cash: float
    wealth: float
    fees_paid: float


@dataclass
class SimulationResult:
    price_history: list[float]
    inventory_history: list[int]
    wealth_history: list[float]
    trade_log: list[TradeLogEntry]
    fees_paid: float


def _build_agent(config: SimulationConfig, strategy: Strategy):
    if strategy is Strategy.NAIVE:
        return NaiveMarketMaker(
            spread=config.naive_spread,
            maker_rebate=config.maker_rebate,
            taker_fee=config.taker_fee,
        )

    if strategy is Strategy.AVELLANEDA_STOIKOV:
        return AvellanedaStoikov(
            T=config.T,
            sigma=config.sigma,
            gamma=config.gamma,
            k=config.k,
            maker_rebate=config.maker_rebate,
            taker_fee=config.taker_fee,
        )

    raise ValueError(f"Unsupported strategy: {strategy}")


def run_simulation(
    config: SimulationConfig,
    strategy: Strategy,
    rng: np.random.Generator | None = None,
) -> SimulationResult:
    env = MarketEnvironment(config, rng=rng)
    agent = _build_agent(config, strategy)
    trade_log = []

    steps = int(config.T / config.dt)

    for _ in range(steps):
        mid_price = env.step_price()
        bid, ask = agent.get_quotes(env.current_time, mid_price)
        bid_filled, ask_filled = env.execute_orders(bid, ask)
        agent.update_state(mid_price, bid_filled, ask_filled, bid, ask)

        trade_log.append(
            TradeLogEntry(
                time=env.current_time,
                mid_price=mid_price,
                bid=bid,
                ask=ask,
                bid_filled=bid_filled,
                ask_filled=ask_filled,
                inventory=agent.inventory,
                cash=agent.cash,
                wealth=agent.wealth_history[-1],
                fees_paid=agent.fees_paid,
            )
        )

    return SimulationResult(
        price_history=env.price_history,
        inventory_history=agent.inventory_history,
        wealth_history=agent.wealth_history,
        trade_log=trade_log,
        fees_paid=agent.fees_paid,
    )

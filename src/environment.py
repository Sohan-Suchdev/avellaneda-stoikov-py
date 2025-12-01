import numpy as np
from dataclasses import dataclass

@dataclass
class MarketConfig:
    T: float = 1.0
    dt: float = 0.005
    sigma: float = 0.5
    start_price: float = 100
    k: float = 1.5  # Kappa
    A: float = 140  # Arrival Intensity

class MarketEnvironment:
    def __init__(self, config: MarketConfig):
        self.config = config
        self.current_time = 0.0
        self.mid_price = config.start_price
        self.price_history = []
        self.time_history = []

    def step_price(self):
        # Geometric Brownian Motion
        dW = np.random.normal(0, np.sqrt(self.config.dt))
        self.mid_price += self.mid_price * self.config.sigma * dW
        self.current_time += self.config.dt
        self.price_history.append(self.mid_price)
        self.time_history.append(self.current_time)
        return self.mid_price

    def execute_orders(self, bid, ask):
        # 1. Calculate Deltas
        delta_bid = self.mid_price - bid
        delta_ask = ask - self.mid_price

        # 2. Calculate Intensity
        lambda_bid = self.config.A * np.exp(-self.config.k * delta_bid)
        lambda_ask = self.config.A * np.exp(-self.config.k * delta_ask)

        # 3. Calculate Probability for this time step
        p_buy = lambda_bid * self.config.dt
        p_sell = lambda_ask * self.config.dt

        # Simulate trade proabbiltity
        bid_filled = np.random.random() < p_buy
        ask_filled = np.random.random() < p_sell

        return bid_filled, ask_filled
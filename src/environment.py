import numpy as np
from src.config import SimulationConfig


class MarketEnvironment:
    def __init__(self, config: SimulationConfig, rng: np.random.Generator | None = None):
        self.config = config
        self.rng = rng if rng is not None else np.random.default_rng()
        self.current_time = 0.0
        self.mid_price = config.start_price
        self.last_return = 0.0
        self.price_history = []
        self.time_history = []

    def step_price(self):
        # Geometric Brownian Motion
        previous_price = self.mid_price
        dW = self.rng.normal(0, np.sqrt(self.config.dt))
        self.mid_price += self.mid_price * self.config.sigma * dW
        self.last_return = (self.mid_price - previous_price) / previous_price
        self.current_time += self.config.dt
        self.price_history.append(self.mid_price)
        self.time_history.append(self.current_time)
        return self.mid_price

    def execute_orders(self, bid, ask):
        if bid is None:
            p_buy = 0.0
        else:
            # 1. Calculate Delta
            delta_bid = self.mid_price - bid

            # 2. Calculate Intensity
            lambda_bid = self.config.A * np.exp(-self.config.k * delta_bid)

            # 3. Calculate Probability for this time step
            p_buy = lambda_bid * self.config.dt

        if ask is None:
            p_sell = 0.0
        else:
            # 1. Calculate Delta
            delta_ask = ask - self.mid_price

            # 2. Calculate Intensity
            lambda_ask = self.config.A * np.exp(-self.config.k * delta_ask)

            # 3. Calculate Probability for this time step
            p_sell = lambda_ask * self.config.dt

        if self.config.adverse_selection_strength:
            adverse_signal = np.sign(self.last_return)
            p_buy *= np.exp(-self.config.adverse_selection_strength * adverse_signal)
            p_sell *= np.exp(self.config.adverse_selection_strength * adverse_signal)

        # These probabilities were previously uncapped; clamp before Bernoulli draws.
        p_buy = np.clip(p_buy, 0.0, 1.0)
        p_sell = np.clip(p_sell, 0.0, 1.0)

        # Simulate trade probability
        bid_filled = self.rng.random() < p_buy
        ask_filled = self.rng.random() < p_sell

        return bid_filled, ask_filled

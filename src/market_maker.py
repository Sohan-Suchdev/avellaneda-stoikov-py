import numpy as np
import math

class MarketMaker:
    def __init__(self, start_cash=0):
        self.cash = start_cash
        self.inventory = 0
        self.inventory_history = []
        self.wealth_history = []

    def update_state(self, current_time, mid_price, bid_filled, ask_filled, fill_price_bid, fill_price_ask):
        # --- FEE STRUCTURE ---
        maker_rebate_pct = 0.0002
        taker_fee_pct = 0.0005

        if bid_filled:
            self.inventory += 1
            if fill_price_bid >= mid_price:
                transaction_cost = fill_price_bid * (1 + taker_fee_pct)
            else:
                transaction_cost = fill_price_bid * (1 - maker_rebate_pct)
            
            self.cash -= transaction_cost

        if ask_filled:
            self.inventory -= 1
            if fill_price_ask <= mid_price:
                revenue = fill_price_ask * (1 - taker_fee_pct)
            else:
                revenue = fill_price_ask * (1 + maker_rebate_pct)
            
            self.cash += revenue
            
        current_wealth = self.cash + (self.inventory * mid_price)
        
        self.inventory_history.append(self.inventory)
        self.wealth_history.append(current_wealth)


class NaiveMarketMaker(MarketMaker):
    def __init__(self, spread=0.5):
        super().__init__()
        self.spread = spread

    def get_quotes(self, current_time, mid_price):
        return mid_price - (self.spread / 2), mid_price + (self.spread / 2)


class AvellanedaStoikov(MarketMaker):
    def __init__(self, T, sigma, gamma, k):
        super().__init__()
        self.T = T
        self.sigma = sigma
        self.gamma = gamma
        self.kappa = k

    def reservation_price(self, mid_price, t):
        time_left = max(self.T - t, 0)
        return mid_price - self.inventory * self.gamma * (self.sigma**2) * time_left

    def optimal_total_spread(self, t):
        time_left = max(self.T - t, 0)
        term1 = self.gamma * (self.sigma**2) * time_left
        term2 = (2.0 / self.gamma) * np.log(1.0 + self.gamma / self.kappa)
        return term1 + term2

    def get_quotes(self, current_time, mid_price):
        r = self.reservation_price(mid_price, current_time)
        delta = self.optimal_total_spread(current_time) / 2.0
        
        bid = r - delta
        ask = r + delta
        
        return bid, ask
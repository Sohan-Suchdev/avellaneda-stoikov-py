import numpy as np


class MarketMaker:
    def __init__(self, maker_rebate, taker_fee, start_cash=0):
        self.cash = start_cash
        self.inventory = 0
        self.maker_rebate = maker_rebate
        self.taker_fee = taker_fee
        # Positive means net fee cost; negative means net rebate earned.
        self.fees_paid = 0.0
        self.inventory_history = [self.inventory]
        self.wealth_history = [self.cash]

    def update_state(self, mid_price, bid_filled, ask_filled, fill_price_bid, fill_price_ask):
        if bid_filled:
            self.inventory += 1
            if fill_price_bid >= mid_price:
                net_fee = fill_price_bid * self.taker_fee
            else:
                net_fee = -fill_price_bid * self.maker_rebate

            self.fees_paid += net_fee
            transaction_cost = fill_price_bid + net_fee
            self.cash -= transaction_cost

        if ask_filled:
            self.inventory -= 1
            if fill_price_ask <= mid_price:
                net_fee = fill_price_ask * self.taker_fee
            else:
                net_fee = -fill_price_ask * self.maker_rebate

            self.fees_paid += net_fee
            revenue = fill_price_ask - net_fee
            self.cash += revenue

        current_wealth = self.cash + (self.inventory * mid_price)

        self.inventory_history.append(self.inventory)
        self.wealth_history.append(current_wealth)


class NaiveMarketMaker(MarketMaker):
    def __init__(self, spread, maker_rebate, taker_fee):
        super().__init__(maker_rebate=maker_rebate, taker_fee=taker_fee)
        self.spread = spread

    def get_quotes(self, current_time, mid_price):
        return mid_price - (self.spread / 2), mid_price + (self.spread / 2)


class AvellanedaStoikov(MarketMaker):
    def __init__(self, T, sigma, gamma, k, maker_rebate, taker_fee):
        super().__init__(maker_rebate=maker_rebate, taker_fee=taker_fee)
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

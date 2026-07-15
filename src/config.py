from dataclasses import dataclass


@dataclass
class SimulationConfig:
    T: float = 1.0
    dt: float = 0.005
    sigma: float = 0.5
    start_price: float = 100
    k: float = 1.5
    A: float = 140
    gamma: float = 1.0
    naive_spread: float = 0.5
    maker_rebate: float = 0.0002
    taker_fee: float = 0.0005
    sharpe_annualization_factor: float = 200

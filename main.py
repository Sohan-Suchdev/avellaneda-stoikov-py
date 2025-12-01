import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.environment import MarketEnvironment, MarketConfig
from src.market_maker import NaiveMarketMaker, AvellanedaStoikov

def run_simulation(strategy_name):
    config = MarketConfig(T=1.0, dt=0.005, sigma=0.5, k=1.5, A=140)
    env = MarketEnvironment(config)
    
    if strategy_name == "Naive":
        agent = NaiveMarketMaker(spread=0.5)
    else:
        agent = AvellanedaStoikov(T=config.T, sigma=config.sigma, gamma=1.0, k=config.k)

    steps = int(config.T / config.dt)
    
    # Simulation Loop
    for _ in range(steps):
        mid_price = env.step_price()
        bid, ask = agent.get_quotes(env.current_time, mid_price)
        bid_filled, ask_filled = env.execute_orders(bid, ask)
        agent.update_state(env.current_time, mid_price, bid_filled, ask_filled, bid, ask)

    return agent, env

def calculate_metrics(agent_wealth):
    series = pd.Series(agent_wealth)
    returns = series.pct_change().dropna()
    if returns.std() == 0: return 0.0, 0.0
    sharpe = (returns.mean() / returns.std()) * np.sqrt(200)
    total_pnl = agent_wealth[-1] - agent_wealth[0]
    return total_pnl, sharpe

if __name__ == "__main__":
    print("Running Simulations...")
    naive_agent, naive_env = run_simulation("Naive")
    as_agent, as_env = run_simulation("Avellaneda-Stoikov")

    naive_pnl, naive_sharpe = calculate_metrics(naive_agent.wealth_history)
    as_pnl, as_sharpe = calculate_metrics(as_agent.wealth_history)
    
    print(f"Naive Strategy: PnL = ${naive_pnl:.2f} | Sharpe = {naive_sharpe:.2f}")
    print(f"AS Strategy:    PnL = ${as_pnl:.2f}   | Sharpe = {as_sharpe:.2f}")

    # Plotting
    fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

    axes[0].plot(as_env.price_history, color='black', label='Market Price', alpha=0.5)
    axes[0].set_title("1. The Market (Geometric Brownian Motion)")
    axes[0].legend()
    axes[0].grid()

    axes[1].plot(naive_agent.inventory_history, label='Naive', color='red', alpha=0.6)
    axes[1].plot(as_agent.inventory_history, label='Avellaneda-Stoikov', color='blue')
    axes[1].set_title("2. Inventory Control")
    axes[1].set_ylabel("Inventory")
    axes[1].legend()
    axes[1].grid()

    axes[2].plot(naive_agent.wealth_history, label=f'Naive (Sharpe: {naive_sharpe:.2f})', color='red', alpha=0.6)
    axes[2].plot(as_agent.wealth_history, label=f'AS (Sharpe: {as_sharpe:.2f})', color='blue')
    axes[2].set_title("3. Cumulative Wealth (PnL with Fees)")
    axes[2].set_ylabel("PnL ($)")
    axes[2].legend()
    axes[2].grid()

    plt.tight_layout()
    plt.show()
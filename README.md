# Digital Market Maker (Stochastic Optimal Control)

A Python-based high-frequency trading simulation that optimises bid-ask spreads using the Avellaneda-Stoikov model to manage inventory risk.

## Project Overview

This project simulates a **Limit Order Book** environment to compare market-making strategies. Unlike directional trading bots that speculate on price movement, this engine acts as a liquidity provider. It quotes two-sided markets to capture the spread while solving the **Inventory Control Problem** via Stochastic Optimal Control.

The simulation models asset prices using **Geometric Brownian Motion** and order flow using **Poisson Processes**, creating a stochastic environment to test the robustness of the famous **Avellaneda-Stoikov** approximation.

## Key Features

### 1. Market Simulation
The simulation creates a realistic closed-loop laboratory:
* **Price Dynamics:** Generates mid-prices using a drift-less random walk ($dS_t = \sigma dW_t$).
* **Order Flow:** Simulates the "Crowd" using Poisson arrival intensities.
* **Fill Probability:** Implements an exponential decay function where the probability of a fill decreases as the spread widens:
    $$P(fill) = A \cdot e^{-k \cdot \delta}$$

### 2. The Agent (Avellaneda-Stoikov Strategy)
Implements the closed-form approximation of the Hamilton-Jacobi-Bellman equation to dynamically adjust quotes:
* **Reservation Price ($r$):** Skews the center price based on current inventory to encourage mean reversion.
* **Optimal Spread ($\delta$):** Widens the spread during periods of high volatility ($\sigma$) or low market liquidity ($k$).

### 3. Execution & Commercial Logic
* **Maker-Taker Fee Structure:** The PnL engine incorporates realistic exchange economics to penalise aggressive inventory management:
    * **Maker Rebate (+0.02%):** Revenue earned when providing passive liquidity (Limit Orders).
    * **Taker Fee (-0.05%):** Cost incurred when crossing the spread (Marketable Limit Orders) to urgently liquidate toxic inventory.
* **Safety Clamps:** Implements logic to prevent negative spreads while enabling the agent to execute "Marketable Limit Orders" when inventory limits are breached, prioritising risk reduction over spread capture.

## Quantitative Theory

### 1. Stochastic Optimal Control
The core objective is to optimise the trade-off between maximising profit and minimising inventory variance. The Avellaneda-Stoikov model dynamically shifts the "reservation price" ($r$) based on current inventory ($q$) and risk aversion ($\gamma$):

$$r(s, q, t) = s - q \gamma \sigma^2 (T - t)$$

### 2. Balancing Risk & Inventory
A Naive market maker utilises a fixed spread strategy that ignores its current position. This often leads to accumulating massive inventory positions that cannot be unwound profitably without incurring heavy losses. This project demonstrates how the AS model calculates a "Reservation Price" that continuously balances the marginal profit of a trade against the inventory risk, allowing the agent to manage its exposure dynamically.

### 3. Market Variance
The optimal spread width ($\delta$) is derived not just from market competition, but from the volatility of the asset and the time remaining in the trading session:

$$\delta = \frac{\gamma \sigma^2 (T-t)}{2} + \frac{2}{\gamma} \ln(1 + \frac{\gamma}{k})$$

## Simulation Results

The simulation performs a comparative backtest between a **Naive Strategy** (Fixed Spread) and the **Avellaneda-Stoikov Strategy** (Stochastic Control).

### Visual Analysis of Strategy Performance
<img width="100%" alt="Simulation Results Dashboard" src="https://github.com/user-attachments/assets/0e62374e-d3c0-495e-9c33-b258304d0ffd" />

### Summary of Observations
The dashboard reveals distinct behaviors between the two agents. The **Naive agent (Red)** acts as a static provider, accumulating unmanaged directional positions which results in a negative PnL (-$18.03). In contrast, the **AS agent (Blue)** exhibits strong mean reversion; when inventory breaches tolerance levels, it aggressively skews prices to neutralise exposure. Despite paying Taker Fees to exit these positions, the AS strategy achieves a significantly higher **Sharpe Ratio (1.05)** and positive Net PnL (+$93.23).

## Technical Stack

* **Python 3.10+**
* **NumPy:** For vectorizing SDE generation (Geometric Brownian Motion).
* **Matplotlib:** For visualizing the 3-panel dashboard (Price Path, Inventory Control, Wealth Accumulation).
* **Pandas:** For calculating annualised Sharpe Ratios and return series.

## Installation & Usage

Clone the repository:
```bash
git clone https://github.com/Sohan-Suchdev/digital-market-maker.git

cd digital-market-maker
```

Setup the environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run the simulation:
```bash
python main.py
```



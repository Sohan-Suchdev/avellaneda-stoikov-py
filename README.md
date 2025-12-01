# Digital Market Maker (Stochastic Optimal Control)

A Python-based high-frequency trading simulation that optimizes bid-ask spreads using the Avellaneda-Stoikov model to manage inventory risk.

## Project Overview

This project simulates a **Limit Order Book (LOB)** environment to compare market-making strategies. Unlike directional trading bots that speculate on price movement, this engine acts as a liquidity provider. It quotes two-sided markets to capture the spread while solving the **Inventory Control Problem** via Stochastic Optimal Control.

The simulation models asset prices using **Geometric Brownian Motion (GBM)** and order flow using **Poisson Processes**, creating a stochastic environment to test the robustness of the famous **Avellaneda-Stoikov (2008)** approximation.

## Key Features

### 1. The Physics Engine (Market Microstructure)
The simulation creates a realistic closed-loop laboratory:
* **Price Dynamics:** Generates mid-prices using a drift-less random walk ($dS_t = \sigma dW_t$).
* **Order Flow:** Simulates the "Crowd" using Poisson arrival intensities.
* **Fill Probability:** Implements an exponential decay function where the probability of a fill decreases as the spread widens:
    $$P(fill) = A \cdot e^{-k \cdot \delta}$$

### 2. The Agent (Avellaneda-Stoikov Strategy)
Implements the closed-form approximation of the Hamilton-Jacobi-Bellman (HJB) equation to dynamically adjust quotes:
* **Reservation Price ($r$):** Skews the center price based on current inventory to encourage mean reversion.
* **Optimal Spread ($\delta$):** Widens the spread during periods of high volatility ($\sigma$) or low market liquidity ($k$).
* **Infinite Horizon Logic:** Applies a "Time Floor" to maintain risk aversion constraints even as the trading session nears value $T$.

### 3. Execution & Commercial Logic
* **Maker-Taker Fee Structure:** The PnL engine accounts for exchange economics:
    * **Maker Rebate (+0.02%):** Earned when providing passive liquidity.
    * **Taker Fee (-0.05%):** Paid when "panic buying" (crossing the spread) to liquidate toxic inventory.
* **Safety Clamps:** Implements logic to prevent negative spreads while allowing aggressive "Marketable Limit Orders" when inventory limits are breached.

## Quantitative Theory

This project is built on three fundamental concepts in Quantitative Finance:

### 1. Stochastic Optimal Control
The core problem is maximizing Utility of Wealth ($U$) while penalizing inventory variance. The Avellaneda-Stoikov model shifts the "fair price" based on inventory ($q$) and risk aversion ($\gamma$):

$$r(s, q, t) = s - q \gamma \sigma^2 (T - t)$$

* **Interpretation:** If the bot is **Long** ($q > 0$), the reservation price $r$ shifts **down**, forcing the Ask price lower to dump inventory aggressively.

### 2. Inventory Risk & Toxic Flow
A Naive market maker quoting a fixed spread around the Mid Price suffers from **Adverse Selection**. In a trending market, they accumulate a massive position against the trend (Toxic Inventory). This project demonstrates how identifying the "Reservation Price" neutralizes this risk.

### 3. Market Variance
The optimal spread width is derived not just from competition, but from the volatility of the asset:

$$\delta = \frac{\gamma \sigma^2 (T-t)}{2} + \frac{2}{\gamma} \ln(1 + \frac{\gamma}{k})$$

## Simulation Results

The engine runs a comparative backtest between a **Naive Strategy** (Fixed Spread) and the **Avellaneda-Stoikov Strategy**.

**1. The Inventory Trap (Naive)**
The Naive agent acts as a "dumb" liquidity provider. As shown in the simulation, it accumulates large positions (e.g., Short -12) and fails to unwind them, leading to massive drawdowns when the price moves against it.

**2. The Mean Reversion (AS)**
The AS agent successfully exhibits **Mean Reversion**. When inventory exceeds $\pm 5$ units, the strategy aggressively skews prices to pay the "Taker Fee" and neutralize exposure.

**3. Performance Metrics**
* **Naive Strategy:** Net PnL: **-$200.50** (Wiped out by holding costs and fees).
* **AS Strategy:** Net PnL: **+$220.15** | **Sharpe Ratio: 1.73**

## The "Liquidation Puzzle" (Technical Challenge)

During development, the AS agent initially failed to liquidate positions at the end of the trading day.
* **Root Cause:** The term $(T-t)$ in the reservation price formula approaches $0$ as time runs out. Mathematically, the model assumed that with 1 second left, there was "zero risk" of price variance, so it stopped skewing prices.
* **Resolution:** I implemented an **Infinite Horizon Assumption** (hardcoding $T-t=1.0$), forcing the bot to treat every second as if it still had significant future risk. This successfully induced the "Panic" behavior required to clear inventory.

## Technical Stack

* **Python 3.10+**
* **NumPy:** For vectorizing SDE generation (Geometric Brownian Motion).
* **Matplotlib:** For visualizing the 3-panel dashboard (Price Path, Inventory Control, Wealth Accumulation).
* **Pandas:** For calculating annualized Sharpe Ratios and return series.

## Installation & Usage

Clone the repository:
```bash
git clone [https://github.com/YourUsername/digital-market-maker.git](https://github.com/YourUsername/digital-market-maker.git)
cd digital-market-maker
# Live Portfolio Risk Engine 

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Redis](https://img.shields.io/badge/Redis-Store-red)
![Status](https://img.shields.io/badge/Status-Prototype-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

##  Overview

This project is a **production-grade prototype** of a Real-Time Risk Management System (RMS) often found in Prime Brokerage and Hedge Funds. 

It acts as a "Risk Engine" that monitors a portfolio of Futures and Options, calculates **Maintenance Margin** in real-time using SPAN-like scenario analysis, and executes **Auto-Liquidation** if the account equity falls below the margin requirement.



##  Key Features

* **Real-Time Architecture:** Decoupled data ingestion and risk calculation using **Redis** as an in-memory state store.
* **Quantitative Modeling:**
    * **Scenario Analysis:** Simulates 14 different market scenarios (Price shocks & Volatility shifts) per tick using **NumPy** vectorization.
    * **Full Valuation:** Uses the **Black-Scholes-Merton** model (via `scipy.stats`) to re-price options across all scenarios (no linear approximations).
* **Type Safety:** Uses **Pydantic** models for strict data validation and serialization.
* **Auto-Liquidation:** Simulates an Order Management System (OMS) trigger to flatten positions immediately upon margin breach.

##  Tech Stack

* **Core Logic:** Python 3.10+
* **Math & Quant:** NumPy, SciPy (Normal Distribution CDF)
* **State Management:** Redis (Dockerized)
* **Validation:** Pydantic
* **Logging:** Python `logging` + Colorama for CLI dashboards

## How It Works (The Logic)
Market Simulation: The system generates a random walk for an underlying asset (e.g., BTC) and updates the volatility surface.

Mark-to-Market (MtM): The portfolio is valued at current market prices.

Stress Testing:

For every position, the engine generates a grid of 14 hypothetical scenarios (e.g., Price -10%, Volatility +50%).

It calculates the theoretical P&L for each scenario using vector math.

Margin Calculation: The "Worst Case Loss" across all scenarios is identified as the Margin Requirement.

Enforcement: If Total Equity < Margin Requirement, the ExecutionService triggers a "Liquidation" event, closing all positions.

##  Disclaimer
For Educational Purposes Only. This software is a simulation designed to demonstrate software engineering and quantitative finance concepts. It is not a certified financial tool and should not be used for actual trading or capital management. The risk models implemented (simplified SPAN/Black-Scholes) do not account for real-world complexities such as liquidity risk, slippage, or extreme tail events beyond the simulation parameters.

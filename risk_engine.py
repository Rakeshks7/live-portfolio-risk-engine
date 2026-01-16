import numpy as np
from models import Position, MarketTick
from config import Config
from pricing import BlackScholes  

class RiskEngine:
    def __init__(self):
        self.price_scenarios = np.array([-1.0, -0.67, -0.33, 0.0, 0.33, 0.67, 1.0])
        self.vol_scenarios = np.array([-1.0, 1.0]) 
        self.risk_free_rate = 0.05  

    def calculate_margin(self, positions: list[Position], market_data: dict[str, MarketTick]) -> float:
        if not positions:
            return 0.0

        total_worst_case_loss = 0.0

        for pos in positions:
            tick = market_data.get(pos.instrument.ticker)
            if not tick:
                continue

            current_price = tick.price
            current_vol = tick.volatility
            
            price_shifts = current_price * Config.SCAN_RANGE_PCT * self.price_scenarios
            sim_prices = current_price + price_shifts

            vol_shift = current_vol * Config.VOL_SCAN_RANGE_PCT
            sim_vols = np.array([current_vol - vol_shift, current_vol + vol_shift])

            if pos.instrument.type == 'future':
                pnl_matrix = (sim_prices - current_price) * pos.quantity
                
                worst_scenario_pnl = np.min(pnl_matrix)

            elif pos.instrument.type == 'option':
                
                P_grid, V_grid = np.meshgrid(sim_prices, sim_vols)
                
                sim_option_prices = BlackScholes.price(
                    S=P_grid,
                    K=pos.instrument.strike,
                    T=pos.instrument.expiry,
                    r=self.risk_free_rate,
                    sigma=V_grid,
                    is_call=pos.instrument.is_call
                )
                
                current_option_val = BlackScholes.price(
                    current_price, pos.instrument.strike, pos.instrument.expiry, 
                    self.risk_free_rate, current_vol, pos.instrument.is_call
                )
                
                pnl_grid = (sim_option_prices - current_option_val) * pos.quantity
                
                worst_scenario_pnl = np.min(pnl_grid)

            if worst_scenario_pnl < 0:
                total_worst_case_loss += abs(worst_scenario_pnl)

        return total_worst_case_loss
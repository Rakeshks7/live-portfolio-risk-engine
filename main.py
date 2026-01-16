import time
import random
import logging
from colorama import Fore, Style, init

from config import Config
from models import Position, Instrument, MarketTick
from database import RedisClient
from risk_engine import RiskEngine
from execution import ExecutionService 
from pricing import BlackScholes

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
init(autoreset=True)

class RiskService:
    def __init__(self):
        self.db = RedisClient()
        self.engine = RiskEngine()
        self.execution = ExecutionService() 
        self.market_state: dict[str, MarketTick] = {}
        
        self.db.r.flushall()
        self._seed_portfolio()

    def _seed_portfolio(self):
        """Injects a mock portfolio."""
        logger.info("Seeding Portfolio...")
        
        pos1 = Position(
            instrument=Instrument(ticker="BTC-FUT", type="future"),
            quantity=2, 
            entry_price=95000.0
        )
        
        pos2 = Position(
            instrument=Instrument(ticker="BTC-DEC-96k-C", type="option", strike=96000, expiry=0.1, is_call=True),
            quantity=-5, 
            entry_price=2500.0 
        )
        
        self.db.add_position(pos1)
        self.db.add_position(pos2)
        self.db.set_equity(Config.INITIAL_EQUITY) 

    def fetch_market_data(self):
        """Simulates live data. We purposely introduce volatility to trigger margin call."""
        if not self.market_state:
            price = 95000.0
            vol = 0.50 
        else:
            prev_price = self.market_state["BTC-FUT"].price
            
            shock = -0.05 if random.random() > 0.95 else random.normalvariate(0, 0.005)
            
            price = prev_price * (1 + shock)
            vol = 0.50 

        self.market_state["BTC-FUT"] = MarketTick(ticker="BTC-FUT", price=price, volatility=vol)
        self.market_state["BTC-DEC-96k-C"] = MarketTick(ticker="BTC-DEC-96k-C", price=price, volatility=vol)

    def run(self):
        logger.info(f"{Fore.CYAN}Starting Risk Engine Microservice...{Style.RESET_ALL}")
        
        while True:
            try:
                self.fetch_market_data()
                current_btc_price = self.market_state["BTC-FUT"].price
                
                positions = self.db.get_all_positions()
                if not positions:
                    print(f"{Fore.YELLOW}No positions. Waiting...{Style.RESET_ALL}")
                    time.sleep(2)
                    continue

                equity_balance = self.db.get_equity()
                
                unrealized_pnl = 0.0
                for pos in positions:
                    tick = self.market_state.get(pos.instrument.ticker)
                    
                    if pos.instrument.type == 'future':
                        val = (tick.price - pos.entry_price) * pos.quantity
                    else:
                        current_opt_price = BlackScholes.price(tick.price, pos.instrument.strike, pos.instrument.expiry, 0.05, tick.volatility, pos.instrument.is_call)
                        val = (current_opt_price - pos.entry_price) * pos.quantity 
                        
                    unrealized_pnl += val
                
                total_equity = equity_balance + unrealized_pnl

                margin_req = self.engine.calculate_margin(positions, self.market_state)
                
                utilization = (margin_req / total_equity) * 100 if total_equity > 0 else 999.99
                
                print(f"\033c", end="") 
                status_color = Fore.GREEN
                if utilization > 80: status_color = Fore.YELLOW
                if utilization > 100: status_color = Fore.RED
                
                print(f"""
{Fore.BLUE}=== LIVE RISK DASHBOARD ==={Style.RESET_ALL}
BTC Price    : ${current_btc_price:,.2f}
Net Equity   : ${total_equity:,.2f}
Margin Req   : ${margin_req:,.2f}
Risk Usage   : {status_color}{utilization:.2f}%{Style.RESET_ALL}
Positions    : {len(positions)}
{'-'*30}
""")

                if total_equity < margin_req:
                    print(f"{Fore.RED}{Style.BRIGHT}!!! MARGIN BREACH DETECTED !!!{Style.RESET_ALL}")
                    self.execution.liquidate_portfolio(positions, reason="Margin Utilization > 100%")
                    time.sleep(5) 
                
                time.sleep(Config.RISK_INTERVAL_SEC)

            except KeyboardInterrupt:
                logger.info("Stopping Risk Engine.")
                break
            except Exception as e:
                logger.error(f"Critical Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    service = RiskService()
    service.run()
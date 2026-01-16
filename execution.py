import logging
import json
from database import RedisClient
from models import Position

logger = logging.getLogger(__name__)

class ExecutionService:
    def __init__(self):
        self.db = RedisClient()

    def liquidate_portfolio(self, positions: list[Position], reason: str):
        if not positions:
            return

        logger.warning(f"EXECUTING LIQUIDATION. REASON: {reason}")

        for pos in positions:
            if pos.quantity == 0:
                continue
            
            action = "SELL" if pos.quantity > 0 else "BUY TO COVER"
            logger.info(f"ORDER SENT: {action} {abs(pos.quantity)} {pos.instrument.ticker} @ MARKET")

            self.db.r.hdel("portfolio:positions", pos.instrument.ticker)
        
        logger.info("LIQUIDATION COMPLETE. PORTFOLIO FLATTENED.")
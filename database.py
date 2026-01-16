import redis
import json
from config import Config
from models import Position

class RedisClient:
    def __init__(self):
        self.r = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB)
    
    def set_equity(self, amount: float):
        self.r.set("account:equity", amount)

    def get_equity(self) -> float:
        val = self.r.get("account:equity")
        return float(val) if val else Config.INITIAL_EQUITY

    def add_position(self, pos: Position):
        self.r.hset("portfolio:positions", pos.instrument.ticker, pos.model_dump_json())

    def get_all_positions(self) -> list[Position]:
        raw_data = self.r.hgetall("portfolio:positions")
        positions = []
        for _, data in raw_data.items():
            positions.append(Position.model_validate_json(data))
        return positions
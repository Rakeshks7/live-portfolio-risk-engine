import os

class Config:
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = 0
    
    SCAN_RANGE_PCT = 0.10      
    VOL_SCAN_RANGE_PCT = 0.15  
    
    INITIAL_EQUITY = 1_000_000.0
    RISK_INTERVAL_SEC = 1      
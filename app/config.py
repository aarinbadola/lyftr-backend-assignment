import os
from functools import lru_cache
class Settings:
    def __init__(self):
        
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////data/app.db")
        self.WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    def __repr__(self):
        return f"Settings(DATABASE_URL={self.DATABASE_URL!r}, WEBHOOK_SECRET={'SET' if self.WEBHOOK_SECRET else 'NOT_SET'}, LOG_LEVEL={self.LOG_LEVEL!r})"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()


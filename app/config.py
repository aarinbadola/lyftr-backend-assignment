# app/config.py
import os
from functools import lru_cache

class Settings:
    """
    Small settings holder that reads from environment variables.
    Kept intentionally minimal and explicit (no third-party dependency),
    which is perfect for small services and CI evaluation scripts.
    """

    def __init__(self):
        # Default DATABASE_URL points to the mounted docker volume path.
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////data/app.db")
        self.WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    def __repr__(self):
        return f"Settings(DATABASE_URL={self.DATABASE_URL!r}, WEBHOOK_SECRET={'SET' if self.WEBHOOK_SECRET else 'NOT_SET'}, LOG_LEVEL={self.LOG_LEVEL!r})"

# cached accessor so importing modules get the same Settings instance
@lru_cache()
def get_settings() -> Settings:
    return Settings()

# convenience instance for simple imports: from app.config import settings
settings = get_settings()


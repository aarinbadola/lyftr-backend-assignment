import logging
import json
from datetime import datetime

logger = logging.getLogger("lyftr")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def iso_ts():
    return datetime.utcnow().isoformat() + "Z"

def log_request(level: str, payload: dict):
    payload = {**payload}
    if "ts" not in payload:
        payload["ts"] = iso_ts()
    payload["level"] = level
    logger.log(logging.INFO if level.lower() == "info" else logging.ERROR, json.dumps(payload, ensure_ascii=False))

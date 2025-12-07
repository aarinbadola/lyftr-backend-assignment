# app/logging_utils.py
import logging
import json
from datetime import datetime

logger = logging.getLogger("lyftr")
handler = logging.StreamHandler()
# simple json formatter via the helper below
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def iso_ts():
    return datetime.utcnow().isoformat() + "Z"

def log_request(level: str, payload: dict):
    """
    Emit a single-line JSON log.
    level: "info", "error", etc.
    payload: dict keys will be serialized into JSON
    """
    payload = {**payload}
    if "ts" not in payload:
        payload["ts"] = iso_ts()
    payload["level"] = level
    # ensure JSON serializable
    logger.log(logging.INFO if level.lower() == "info" else logging.ERROR, json.dumps(payload, ensure_ascii=False))

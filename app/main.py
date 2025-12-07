import uuid
import time
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from .models import init_db, db_is_ready
from .config import settings
from .security import compute_signature
from .schemas import WebhookMessage
from .storage import insert_message
from .logging_utils import log_request
import hmac as _hmac  
from .storage import query_messages
from fastapi import Query
from typing import Optional
from .storage import count_total_messages, messages_by_day, messages_by_sender

app = FastAPI()

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/health/live")
def live():
    return {"status": "ok"}

@app.get("/health/ready")
def ready():
    secret_ok = bool(settings.WEBHOOK_SECRET)
    db_ok = db_is_ready()
    if secret_ok and db_ok:
        return {"status": "ok"}
    return JSONResponse(status_code=503, content={"status": "not ready", "db_ok": db_ok, "secret_ok": secret_ok})
@app.get("/stats")
def get_stats(
    start_ts: Optional[str] = None,
    end_ts: Optional[str] = None,
    days: Optional[int] = None,     
    top: int = 10                   
):
    
    total = count_total_messages(start_ts=start_ts, end_ts=end_ts)
    by_day = messages_by_day(start_ts=start_ts, end_ts=end_ts, days=days)
    top_senders = messages_by_sender(limit=top, start_ts=start_ts, end_ts=end_ts)

    return {
        "total_messages": total,
        "messages_by_day": [{"date": d, "count": c} for d, c in by_day],
        "top_senders": [{"from_msisdn": f, "count": c} for f, c in top_senders],
    }

@app.post("/webhook")
async def webhook(request: Request, x_signature: str | None = Header(None, alias="X-Signature")):
    request_id = str(uuid.uuid4())
    start = time.time()
    raw = await request.body() 
 
    base_log = {
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
    }

    if not x_signature:
        log_request("error", {**base_log, "status": 401, "result": "invalid_signature"})
        raise HTTPException(status_code=401, detail="invalid signature")

    
    expected = compute_signature(settings.WEBHOOK_SECRET, raw)
    # use constant-time compare
    if not _hmac.compare_digest(expected, x_signature):
        log_request("error", {**base_log, "status": 401, "result": "invalid_signature"})
        raise HTTPException(status_code=401, detail="invalid signature")

    try:
        
        body_text = raw.decode("utf-8")
        msg = WebhookMessage.model_validate_json(body_text)
    except Exception as exc:
        
        log_request("error", {**base_log, "status": 422, "result": "validation_error", "error": str(exc)})
        raise

    inserted = insert_message(msg.message_id, msg.from_, msg.to, msg.ts, msg.text)
    dup = not inserted
    result = "duplicate" if dup else "created"

    latency_ms = int((time.time() - start) * 1000)
    log_payload = {
        **base_log,
        "status": 200,
        "latency_ms": latency_ms,
        "message_id": msg.message_id,
        "dup": dup,
        "result": result,
    }
    log_request("info", log_payload)

    return JSONResponse(status_code=200, content={"status": "ok"})
@app.get("/messages")
def get_messages(
    from_: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None),
    start_ts: Optional[str] = Query(None),
    end_ts: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    order: str = Query("desc", regex="^(asc|desc)$", description="Sort by ts: asc or desc"),
):
    
    filters = {}
    if from_:
        filters["from_msisdn"] = from_
    if to:
        filters["to_msisdn"] = to
    if start_ts:
        filters["start_ts"] = start_ts
    if end_ts:
        filters["end_ts"] = end_ts

    items, total = query_messages(page=page, per_page=per_page, order=order, **filters)
    pages = (total + per_page - 1) // per_page if per_page else 1

    return {
        "items": items,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages
        }
    }

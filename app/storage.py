# app/storage.py
from .models import get_conn
from datetime import datetime

def insert_message(message_id: str, from_msisdn: str, to_msisdn: str, ts: str, text: str) -> bool:
    """
    Insert a message idempotently.
    Returns True if a new row was created, False if a duplicate was detected.
    """
    conn = get_conn()
    try:
        created_at = datetime.utcnow().isoformat() + "Z"
        # Use INSERT OR IGNORE to avoid raising on duplicate primary key
        cur = conn.execute(
            "INSERT OR IGNORE INTO messages(message_id, from_msisdn, to_msisdn, ts, text, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (message_id, from_msisdn, to_msisdn, ts, text, created_at),
        )
        conn.commit()
        # rowcount is 1 when a row was inserted, 0 when ignored (duplicate)
        return cur.rowcount == 1
    finally:
        conn.close()

def message_exists(message_id: str) -> bool:
    conn = get_conn()
    try:
        cur = conn.execute("SELECT 1 FROM messages WHERE message_id = ? LIMIT 1", (message_id,))
        return cur.fetchone() is not None
    finally:
        conn.close()
# app/storage.py
# (keep the existing imports and insert these functions)

def _build_filters_sql(params: dict):
    """
    Build WHERE clause and an args tuple for parameterized queries.
    params keys allowed: from_msisdn, to_msisdn, start_ts, end_ts
    Returns (where_sql, args_list)
    """
    where_clauses = []
    args = []

    if params.get("from_msisdn"):
        where_clauses.append("from_msisdn = ?")
        args.append(params["from_msisdn"])

    if params.get("to_msisdn"):
        where_clauses.append("to_msisdn = ?")
        args.append(params["to_msisdn"])

    if params.get("start_ts"):
        where_clauses.append("ts >= ?")
        args.append(params["start_ts"])

    if params.get("end_ts"):
        where_clauses.append("ts <= ?")
        args.append(params["end_ts"])

    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    return where_sql, args

def count_messages_filtered(**filters) -> int:
    """
    Count total messages matching the optional filters.
    filters: from_msisdn, to_msisdn, start_ts, end_ts
    """
    conn = get_conn()
    try:
        where_sql, args = _build_filters_sql(filters)
        q = "SELECT COUNT(*) as cnt FROM messages" + where_sql
        cur = conn.execute(q, args)
        r = cur.fetchone()
        return r["cnt"] if r else 0
    finally:
        conn.close()

def query_messages(page: int = 1, per_page: int = 20, order: str = "desc", **filters):
    """
    Query messages with pagination and filters.
    Returns (items_list, total_count).
    """
    # sanitize order
    order_sql = "DESC" if order.lower() != "asc" else "ASC"

    # build filters
    where_sql, args = _build_filters_sql(filters)

    # pagination math
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 20
    offset = (page - 1) * per_page

    conn = get_conn()
    try:
        # fetch total count
        count_q = "SELECT COUNT(*) AS cnt FROM messages" + where_sql
        total = conn.execute(count_q, args).fetchone()["cnt"]

        # fetch page
        q = f"""
        SELECT message_id, from_msisdn, to_msisdn, ts, text, created_at
        FROM messages
        {where_sql}
        ORDER BY ts {order_sql}
        LIMIT ? OFFSET ?
        """
        page_args = args[:]  # copy
        page_args.extend([per_page, offset])
        cur = conn.execute(q, page_args)
        rows = cur.fetchall()
        # convert sqlite3.Row to dict
        items = [dict(r) for r in rows]
        return items, total
    finally:
        conn.close()
# app/storage.py
from datetime import datetime, timedelta

def count_total_messages(start_ts: str | None = None, end_ts: str | None = None, from_msisdn: str | None = None, to_msisdn: str | None = None) -> int:
    conn = get_conn()
    try:
        where, args = _build_filters_sql({
            "start_ts": start_ts,
            "end_ts": end_ts,
            "from_msisdn": from_msisdn,
            "to_msisdn": to_msisdn,
        })
        q = "SELECT COUNT(*) AS cnt FROM messages" + where
        r = conn.execute(q, args).fetchone()
        return r["cnt"] if r else 0
    finally:
        conn.close()

def messages_by_day(start_ts: str | None = None, end_ts: str | None = None, days: int | None = None):
    """
    Returns list of (date_str, count) grouped by date (YYYY-MM-DD), ordered ASC by date.
    If `days` is provided, returns last `days` days up to today (UTC).
    Otherwise uses start_ts/end_ts if provided, or full table.
    """
    conn = get_conn()
    try:
        # compute window if days provided
        if days is not None:
            # compute start_ts as days back (UTC), inclusive
            dt_end = datetime.utcnow()
            dt_start = dt_end - timedelta(days=days-1)
            start_ts = dt_start.isoformat() + "Z"
            end_ts = dt_end.isoformat() + "Z"

        where, args = _build_filters_sql({"start_ts": start_ts, "end_ts": end_ts})
        q = f"""
        SELECT substr(ts,1,10) AS day, COUNT(*) AS cnt
        FROM messages
        {where}
        GROUP BY day
        ORDER BY day ASC
        """
        rows = conn.execute(q, args).fetchall()
        return [(r["day"], r["cnt"]) for r in rows]
    finally:
        conn.close()

def messages_by_sender(limit: int = 10, start_ts: str | None = None, end_ts: str | None = None):
    """
    Returns top senders (from_msisdn) with counts, ordered desc by count.
    """
    conn = get_conn()
    try:
        where, args = _build_filters_sql({"start_ts": start_ts, "end_ts": end_ts})
        q = f"""
        SELECT from_msisdn, COUNT(*) AS cnt
        FROM messages
        {where}
        GROUP BY from_msisdn
        ORDER BY cnt DESC
        LIMIT ?
        """
        q_args = args[:] + [limit]
        rows = conn.execute(q, q_args).fetchall()
        return [(r["from_msisdn"], r["cnt"]) for r in rows]
    finally:
        conn.close()

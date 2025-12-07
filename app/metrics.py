from datetime import datetime
from collections import Counter, defaultdict
from .models import get_db_connection

def get_total_messages():
    
    conn = get_db_connection()
    cur = conn.execute("SELECT COUNT(*) FROM messages;")
    total = cur.fetchone()[0]
    conn.close()
    return total

def get_messages_by_day():
    
    conn = get_db_connection()
    cur = conn.execute("SELECT ts FROM messages;")
    rows = cur.fetchall()
    conn.close()

    day_counts = defaultdict(int)
    for (ts,) in rows:
        try:
            date = datetime.fromisoformat(ts.replace("Z", "")).date().isoformat()
            day_counts[date] += 1
        except Exception:
            continue

    return [{"date": d, "count": c} for d, c in sorted(day_counts.items())]


def get_top_senders(limit=5):
    conn = get_db_connection()
    cur = conn.execute("SELECT from_msisdn FROM messages;")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()

    count = Counter(rows).most_common(limit)

    return [{"from_msisdn": msisdn, "count": c} for msisdn, c in count]


def get_stats():

    return {
        "total_messages": get_total_messages(),
        "messages_by_day": get_messages_by_day(),
        "top_senders": get_top_senders(),
    }

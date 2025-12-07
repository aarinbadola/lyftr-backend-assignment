# Lyftr Backend Assignment  
A backend service built using **FastAPI**, **SQLite**, and **Docker** to receive webhook events, verify signatures, store messages, and expose reporting APIs.

---

##Features Implemented

### 1. Webhook Receiver (`POST /webhook`)
- Accepts incoming JSON webhook payloads.
- Validates request signatures using HMAC SHA-256.
- Ensures **idempotency** — duplicated webhook events are ignored.
- Stores valid messages in SQLite.

###  2. Message Storage
- Messages stored in a persistent SQLite DB (`/data/app.db`).
- Schema includes:
  - `message_id`
  - `from_msisdn`
  - `to_msisdn`
  - `ts` (timestamp)
  - `text`
  - `created_at`

###  3. Message Listing (`GET /messages`)
- Paginated response (page, per_page).
- Returns items + pagination metadata.

###  4. Reporting API (`GET /stats`)
Provides:
- **Total messages received**
- **Messages grouped by day**
- **Top senders with count**

###  5. Health Endpoints
- `/health/live` -service is up  
- `/health/ready` -database connection ready

### 6. Fully Dockerized
- Run everything using Docker Compose
- Persistent volume for SQLite

---

##  Tech Stack

- **Python 3.11**
- **FastAPI**
- **Uvicorn**
- **SQLite**
- **Docker + Docker Compose**
- **Pydantic (v2)**
- **HMAC Signature Verification**

---

RUNNING THE LYFTR BACKEND
1)Build & Start the Backend in Docker
Run from the project root:
 docker compose up -d --build

2)Health Check Endpoints
Liveness: curl http://localhost:8000/health/live
   Expected:{"status": "ok"}
Readiness:curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/ready
   Expected:200

3)Sending a Webhook Request (Signed)
Step A — Create a sample body:
   {
    "message_id": "m1",
    "from": "+919876543210",
    "to": "+14155550100",
    "timestamp": "2025-01-15T10:00:00Z",
    "text": "Hello"
}

Step B — Generate signature
Inside the project root, run: python sign.py

Step C — Send webhook POST
curl -H "Content-Type: application/json" ^
     -H "X-Signature: <YOUR_SIGNATURE>" ^
     --data-binary @body.json ^
     http://localhost:8000/webhook -v

Expected: {"status": "accepted"}

4)Check Stored Messages
  curl "http://localhost:8000/messages"

5)View Stats
  curl "http://localhost:8000/stats"

6)Stop the App
  docker compose down


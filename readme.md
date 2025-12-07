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




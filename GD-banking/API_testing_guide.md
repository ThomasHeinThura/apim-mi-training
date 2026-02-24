# GD-Banking API Testing Guide

## What was verified from your existing setup

- Java backend API path: `POST /api/banking/transaction`
- Java backend API paths: `POST /api/banking/transaction`, `GET /api/banking/balance/{userId}`, `GET /api/banking/history/{userId}`
- Java backend base (docker compose host): `http://localhost:5004`
- Guaranteed delivery store table in MySQL: `banking_db.jdbc_message_store`
- Table creation is already in: `apim-mi-docker/mysql/scripts/banking_init.sql`

## MI APIs added in GD-banking

### BankingProxyApi (single API)

- API context: `/banking`
- `POST /transaction` → guaranteed delivery (queued in MySQL table `jdbc_message_store`, replayed by message processor)
- `GET /balance/{userId}` → forwards to Java backend balance API
- `GET /history/{userId}` → forwards to Java backend history API
- `GET /users/summary` → reads directly from MySQL `banking_db.users`

### MySQL direct summary API via MI

- API context: `/banking`
- `GET /users/summary`
- Reads directly from MySQL `banking_db.users` and returns:
  - `totalUsers`
  - `totalAmount` (sum of all user balances)

Example:

```bash
curl -s "http://localhost:8290/banking/users/summary"
```

Expected response:

```json
{"totalUsers":100,"totalAmount":100000.00}
```

## Test scenario: backend down, then up

### 1) Start stack

Ensure MySQL, MI, and Java app are normally reachable first.

### 2) Stop Java backend

```bash
docker stop java-app
```

### 3) Send transaction to MI (should be queued)

```bash
curl -i -X POST "http://localhost:8290/banking/transaction" \
  -H "Content-Type: application/json" \
  -d '{"userId":1,"amount":25.00,"type":"DEBIT"}'
```

Expected: HTTP `202` with body similar to:

```json
{"status":"QUEUED","message":"Transaction queued for guaranteed delivery"}
```

### 4) Verify message stored in MySQL

```bash
docker exec -it demo-mysql mysql -uroot -proot -e "USE banking_db; SELECT COUNT(*) AS queued_count FROM jdbc_message_store;"
```

Expected: `queued_count` should be greater than `0` while backend is down.

### 5) Start Java backend again

```bash
docker start java-app
```

### 6) Wait for replay

Message processor interval is 5 seconds. Wait ~10-20 seconds.

### 7) Verify queue drained and transaction applied

Check queue table:

```bash
docker exec -it demo-mysql mysql -uroot -proot -e "USE banking_db; SELECT COUNT(*) AS queued_count FROM jdbc_message_store;"
```

Check backend history:

```bash
curl -s "http://localhost:5004/api/banking/history/1"
```

You should see the replayed transaction in history after backend is up.

## Important note

Yes — your understanding is correct for this setup:
- When backend is down, your POST to MI is accepted and stored.
- When backend comes back, message processor retries and sends the message.

## Quick tests for original 3 APIs via MI

```bash
# 1) POST transaction via MI (guaranteed delivery)
curl -s -X POST "http://localhost:8290/banking/transaction" \
  -H "Content-Type: application/json" \
  -d '{"userId":1,"amount":10.00,"type":"CREDIT"}'

# 2) GET balance via MI direct proxy
curl -s "http://localhost:8290/banking/balance/1"

# 3) GET history via MI direct proxy
curl -s "http://localhost:8290/banking/history/1"
```

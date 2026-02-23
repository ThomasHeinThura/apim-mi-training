# API Testing Guide

This guide explains how to test all backend APIs after running the standalone stack from `apim-mi-docker`.

## 1) Start the stack

From the `apim-mi-docker` folder:

```bash
docker compose up -d
docker compose ps
```

Make sure services are `Up` (and health checks are healthy where defined).

## 2) Test MySQL seed data

```bash
docker exec demo-mysql mysql -uroot -proot -e "SELECT COUNT(*) AS users_count FROM banking_db.users;"
```

Expected: `users_count` should be at least `100`.

## 3) Backend API smoke tests

### 3.1 Demo APIs (.NET)

```bash
curl -i "http://localhost:5001/api/v1/customerdetails?customerCode=CIF001"
```

Expected: `HTTP/1.1 200` with customer details JSON.

### 3.2 Dotnet Banking App (.NET)

```bash
curl -i "http://localhost:5002/api/portal/user/user1"
```

Expected: `HTTP/1.1 200` with user profile JSON.

### 3.3 Guaranteed Delivery (Python)

```bash
curl -i "http://localhost:5003/api/v1/customerdetails?customerCode=CIF001"
```

Expected: `HTTP/1.1 200` with customer/account JSON.

### 3.4 Java Banking App (Spring Boot)

This API is protected by API key.

```bash
curl -i -H "X-API-KEY: TEST-API-KEY-12345" "http://localhost:5004/api/banking/balance/1"
```

Expected: `HTTP/1.1 200`.

If header is missing, expected response is `401 Unauthorized`.

### 3.5 WSO2 Demo APIs (Python)

```bash
curl -i -X POST "http://localhost:5005/api/v1/kyc/check-blacklist" \
  -H "Content-Type: application/json" \
  -d '{"id":"123"}'
```

Expected: `HTTP/1.1 200` with blacklist result JSON.

## 4) One-shot smoke test commands

```bash
curl -s -o /dev/null -w "demoapis:%{http_code}\n" "http://localhost:5001/api/v1/customerdetails?customerCode=CIF001"
curl -s -o /dev/null -w "dotnet-app:%{http_code}\n" "http://localhost:5002/api/portal/user/user1"
curl -s -o /dev/null -w "guaranteed-delivery:%{http_code}\n" "http://localhost:5003/api/v1/customerdetails?customerCode=CIF001"
curl -s -o /dev/null -w "java-app:%{http_code}\n" -H "X-API-KEY: TEST-API-KEY-12345" "http://localhost:5004/api/banking/balance/1"
curl -s -o /dev/null -w "wso2demoapis:%{http_code}\n" -X POST "http://localhost:5005/api/v1/kyc/check-blacklist" -H "Content-Type: application/json" -d '{"id":"123"}'
```

Expected: all services return `200`.

## 5) Troubleshooting

- Check container state:

```bash
docker compose ps
```

- Check logs for specific service:

```bash
docker compose logs --tail=200 <service-name>
```

- Restart one service:

```bash
docker compose restart <service-name>
```

- Recreate full stack:

```bash
docker compose down --remove-orphans
docker compose up -d
```
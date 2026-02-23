# API Testing Guide

This guide is organized exactly as requested:

1. Normal backend APIs (direct service URLs + output)
2. APIs from MI (URLs + output)
3. APIs from APIM (URLs + expected output)

## 1) Prerequisite

From `apim-mi-docker`:

```bash
docker compose up -d
docker compose ps
```

---

## 2) Normal backend APIs URL and output

### 2.1 Java Banking App (direct to backend)

URL:

```bash
curl -s -H "X-API-KEY: TEST-API-KEY-12345" "http://localhost:5004/api/banking/balance/1"
```

Sample output:

```json
{"id":1,"username":"user1","email":"user1@example.com","balance":1000.00,"createdAt":"2026-02-23T18:32:08"}
```

### 2.2 Dotnet Banking App (direct to backend)

URL:

```bash
curl -s "http://localhost:5002/api/portal/user/user1"
```

Sample output:

```json
{"id":1,"username":"user1","email":"user1@example.com","balance":1000.00,"createdAt":"2026-02-23T18:32:08"}
```

### 2.3 Guaranteed Delivery backend (direct to backend)

URL:

```bash
curl -s "http://localhost:5003/api/v1/customerdetails?customerCode=CIF001"
```

Sample output:

```json
{"accounts":[{"balance":1000.0,"iban":"GB00AAAA00000000000000"}],"customerCode":"CIF001","name":"John Doe"}
```

### 2.4 WSO2DemoApis backend (direct to backend)

URLs:

```bash
curl -s -X POST "http://localhost:5005/api/v1/kyc/check-blacklist" -H "Content-Type: application/json" -d '{"id":"123"}'
curl -s -X POST "http://localhost:5005/api/v1/kyc/check-onboarded" -H "Content-Type: application/json" -d '{"id":"123"}'
```

Sample output:

```json
{"blacklisted":false,"details":{"id":"123"}}
{"onboarded":true,"details":{"id":"123"}}
```

### 2.5 SOAP Banking backend (direct SOAP)

URL:

```bash
curl -s -X POST "http://localhost:5006/soap" \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ban="urn:banking:soap"><soapenv:Header/><soapenv:Body><ban:GetBalanceRequest><ban:AccountId>1001</ban:AccountId></ban:GetBalanceRequest></soapenv:Body></soapenv:Envelope>'
```

Sample output:

```xml
<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ban="urn:banking:soap"><soapenv:Header/><soapenv:Body><ban:GetBalanceResponse><ban:AccountId>1001</ban:AccountId><ban:Balance>12500.50</ban:Balance><ban:Currency>USD</ban:Currency><ban:Status>ACTIVE</ban:Status></ban:GetBalanceResponse></soapenv:Body></soapenv:Envelope>
```

### 2.6 Swagger Petstore backend (direct)

URL:

```bash
curl -s "http://localhost:5007/api/v3/openapi.json"
```

Sample output (truncated):

```json
{"openapi":"3.0.4","info":{"title":"Swagger Petstore","description":"This is a sample server Petstore server.","version":"1.0.28"}}
```

---

## 3) APIs from MI URL and output

### 3.1 GuaranteedDeliveryDemo via MI

URL:

```bash
curl -s -X POST "http://localhost:8290/getcustomerdetails" -H "Content-Type: application/json" -d '{}'
```

Sample output:

```json
{"accounts":[{"balance":1000.0,"iban":"GB00AAAA00000000000000"}],"customerCode":"CIF001","name":"John Doe"}
```

### 3.2 WSO2DemoApis via MI (KYC)

URL:

```bash
curl -s -X POST "http://localhost:8290/checkkyc" -H "Content-Type: application/json" -d '{"nrc":"12/AhSaNa(N)999999"}'
```

Sample output:

```json
{"blacklisted":false,"details":{"nrc":"12/AhSaNa(N)999999"}}
```

### 3.3 WSO2DemoApis via MI (SMS routing)

URL:

```bash
curl -s -X POST "http://localhost:8290/smsgateway" -H "Content-Type: application/json" -d '{"mobileNumber":"09751234567"}'
```

Sample output:

```json
{"operator":"atom","status":"ok"}
```

### 3.4 WSO2DemoApis via MI (multi API call)

URL:

```bash
curl -s "http://localhost:8290/multiapicall"
```

Current output:

```json
{"Customer":{"firstName":"","lastName":"","nrc":"","email":""},"Account":{"accountNumber":"","accountType":""}}
```

### 3.5 SOAP backend mapped by MI as REST API

URL:

```bash
curl -s "http://localhost:8290/soapbanking/balance/1001"
```

Sample output:

```json
{
  "accountId": "1001",
  "balance": "12500.50",
  "currency": "USD",
  "status": "ACTIVE"
}
```

---

## 4) APIs from APIM URL and output

After importing and publishing APIs in APIM, use gateway URL through nginx:

- APIM Publisher UI: `https://am-uat.example.com:443/publisher/`
- APIM Gateway base: `https://api-uat.example.com:443`

If you are testing locally, use host mapping in curl:

```bash
curl -k --resolve api-uat.example.com:443:127.0.0.1 "https://api-uat.example.com:443/<api-context>/<version>/<resource>"
```

### 4.1 Java Banking imported directly to APIM

Example URL (adjust to your published context/version):

```bash
curl -k --resolve api-uat.example.com:443:127.0.0.1 \
  "https://api-uat.example.com:443/java-banking/1.0.0/api/banking/balance/1" \
  -H "X-API-KEY: TEST-API-KEY-12345"
```

Expected output (same as backend):

```json
{"id":1,"username":"user1","email":"user1@example.com","balance":1000.00,"createdAt":"2026-02-23T18:32:08"}
```

### 4.2 Dotnet Banking imported directly to APIM

Example URL:

```bash
curl -k --resolve api-uat.example.com:443:127.0.0.1 \
  "https://api-uat.example.com:443/dotnet-banking/1.0.0/api/portal/user/user1"
```

Expected output (same as backend):

```json
{"id":1,"username":"user1","email":"user1@example.com","balance":1000.00,"createdAt":"2026-02-23T18:32:08"}
```

### 4.3 GuaranteedDeliveryDemo imported to MI then APIM

Example URL:

```bash
curl -k --resolve api-uat.example.com:443:127.0.0.1 \
  -X POST "https://api-uat.example.com:443/gd-mi/1.0.0/getcustomerdetails" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Expected output (same as MI):

```json
{"accounts":[{"balance":1000.0,"iban":"GB00AAAA00000000000000"}],"customerCode":"CIF001","name":"John Doe"}
```

### 4.4 WSO2DemoApis imported to MI then APIM

Example URL:

```bash
curl -k --resolve api-uat.example.com:443:127.0.0.1 \
  -X POST "https://api-uat.example.com:443/wso2demo-mi/1.0.0/checkkyc" \
  -H "Content-Type: application/json" \
  -d '{"nrc":"12/AhSaNa(N)999999"}'
```

Expected output (same as MI):

```json
{"blacklisted":false,"details":{"nrc":"12/AhSaNa(N)999999"}}
```

### 4.5 SOAP backend (through MI) imported to APIM

Example URL:

```bash
curl -k --resolve api-uat.example.com:443:127.0.0.1 \
  "https://api-uat.example.com:443/soapbanking-mi/1.0.0/soapbanking/balance/1001"
```

Expected output (same as MI):

```json
{
  "accountId": "1001",
  "balance": "12500.50",
  "currency": "USD",
  "status": "ACTIVE"
}
```

### 4.6 Swagger Petstore imported directly to APIM

Example URL:

```bash
curl -k --resolve api-uat.example.com:443:127.0.0.1 \
  "https://api-uat.example.com:443/petstore/1.0.0/api/v3/openapi.json"
```

Expected output: OpenAPI JSON for Petstore.
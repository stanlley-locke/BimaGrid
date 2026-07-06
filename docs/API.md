# BimaGrid — API Reference & curl Testing Guide

> Complete documentation for all BimaGrid REST API endpoints with ready-to-run curl examples.

---

## Base URLs

| Environment | URL |
|---|---|
| **Development (Django direct)** | `http://localhost:8000` |
| **Development (via Gateway)** | `http://localhost:3001` |
| **Production** | `https://api.bimagrid.io` |

All API endpoints are prefixed with `/api/v1/`.

---

## Authentication

BimaGrid uses **JWT Bearer Tokens** (via DRF SimpleJWT).

### Obtain Access Token

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "farmer@example.com",
    "password": "yourpassword"
  }'
```

**Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Set the token for subsequent requests:
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Refresh Access Token

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/refresh/ \
  -H 'Content-Type: application/json' \
  -d '{"refresh": "eyJhbGciOi..."}'
```

---

## 1. Authentication Endpoints

### `POST /api/v1/auth/register/`
Register a new user account.

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "farmer@example.com",
    "email": "farmer@example.com",
    "password": "StrongP@ss123",
    "password_confirm": "StrongP@ss123",
    "first_name": "Amina",
    "last_name": "Ochieng",
    "phone": "+254711234567"
  }'
```

**201 Created:**
```json
{
  "id": "a1b2c3d4-...",
  "username": "farmer@example.com",
  "email": "farmer@example.com",
  "first_name": "Amina",
  "last_name": "Ochieng",
  "phone": "+254711234567"
}
```

**400 Bad Request:**
```json
{"password": ["This password is too short."]}
```

---

### `POST /api/v1/auth/token/`
Obtain JWT access + refresh tokens.

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "farmer@example.com", "password": "StrongP@ss123"}'
```

**401 Unauthorized:**
```json
{"detail": "No active account found with the given credentials"}
```

---

## 2. Farmer Account Endpoints

### `GET /api/v1/accounts/me/`
Get the current authenticated user's profile.

```bash
curl -s http://localhost:8000/api/v1/accounts/me/ \
  -H "Authorization: Bearer $TOKEN"
```

**200 OK:**
```json
{
  "id": "a1b2c3d4-...",
  "username": "farmer@example.com",
  "first_name": "Amina",
  "last_name": "Ochieng",
  "phone": "+254711234567",
  "national_id": "12345678",
  "mpesa_number": "254711234567",
  "ward": "Kisumu Central",
  "ward_code": "WARD-KISUMU-01",
  "date_joined": "2026-07-02T06:00:00Z"
}
```

---

### `PATCH /api/v1/accounts/me/`
Update profile fields.

```bash
curl -s -X PATCH http://localhost:8000/api/v1/accounts/me/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"mpesa_number": "254700999888", "ward_code": "WARD-KISUMU-02"}'
```

---

## 3. Policy Endpoints

### `GET /api/v1/policies/`
List all policies for the authenticated farmer.

```bash
curl -s http://localhost:8000/api/v1/policies/ \
  -H "Authorization: Bearer $TOKEN"
```

**200 OK:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 123,
      "policy_number": "POL-20260702-0001",
      "crop": "MAIZE",
      "acreage": "2.50",
      "ward": "Kisumu Central",
      "h3_index": "8928308280fffff",
      "threshold_mm": "20.00",
      "payout_amount_kes": "15000.00",
      "premium_kes": "1200.00",
      "status": "ACTIVE",
      "is_active": true,
      "paid_out": false,
      "start_date": "2026-04-01",
      "end_date": "2026-09-30"
    }
  ]
}
```

---

### `POST /api/v1/policies/`
Create a new parametric insurance policy.

```bash
curl -s -X POST http://localhost:8000/api/v1/policies/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "crop": "MAIZE",
    "acreage": 2.5,
    "ward_code": "WARD-KISUMU-01",
    "season": "LONG_RAINS_2026",
    "mitigation_techniques": ["drip_irrigation"]
  }'
```

**201 Created:**
```json
{
  "id": 124,
  "policy_number": "POL-20260702-0002",
  "h3_index": "8928308280fffff",
  "threshold_mm": "20.00",
  "payout_amount_kes": "15000.00",
  "premium_kes": "1020.00",
  "discount_applied": "15.00",
  "status": "PENDING_PAYMENT",
  "stk_push_sent": true
}
```

---

### `GET /api/v1/policies/{id}/`
Get details for a single policy.

```bash
curl -s http://localhost:8000/api/v1/policies/123/ \
  -H "Authorization: Bearer $TOKEN"
```

---

### `GET /api/v1/policies/{id}/status/`
Get the current claim/payout status for a policy.

```bash
curl -s http://localhost:8000/api/v1/policies/123/status/ \
  -H "Authorization: Bearer $TOKEN"
```

**200 OK:**
```json
{
  "policy_id": 123,
  "status": "ACTIVE",
  "last_oracle_reading_mm": "14.50",
  "last_evaluation": "2026-07-02T23:05:00Z",
  "days_below_threshold": 3,
  "payout_triggered": false
}
```

---

## 4. Onboarding Endpoints

### `POST /api/v1/onboarding/register-farmer/`
Full farmer onboarding — identity verification + policy quote.

```bash
curl -s -X POST http://localhost:8000/api/v1/onboarding/register-farmer/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "national_id": "12345678",
    "phone": "+254711234567",
    "mpesa_number": "254711234567",
    "ward_code": "WARD-KISUMU-01",
    "gps_lat": -0.091702,
    "gps_lng": 34.767956,
    "land_parcel_number": "KISUMU/123/456"
  }'
```

---

### `POST /api/v1/onboarding/verify-identity/`
Verify National ID against IPRS.

```bash
curl -s -X POST http://localhost:8000/api/v1/onboarding/verify-identity/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"national_id": "12345678", "date_of_birth": "1985-03-15"}'
```

**200 OK:**
```json
{"verified": true, "name": "AMINA OCHIENG", "status": "VERIFIED"}
```

---

### `GET /api/v1/onboarding/status/`
Check onboarding completion status.

```bash
curl -s http://localhost:8000/api/v1/onboarding/status/ \
  -H "Authorization: Bearer $TOKEN"
```

**200 OK:**
```json
{
  "identity_verified": true,
  "land_verified": true,
  "policy_active": true,
  "onboarding_complete": true,
  "completion_percentage": 100
}
```

---

## 5. Claims Endpoints

### `GET /api/v1/claims/`
List all claims for the authenticated farmer.

```bash
curl -s http://localhost:8000/api/v1/claims/ \
  -H "Authorization: Bearer $TOKEN"
```

---

### `POST /api/v1/claims/`
File a manual claim (note: parametric claims are auto-triggered).

```bash
curl -s -X POST http://localhost:8000/api/v1/claims/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "policy_id": 123,
    "loss_type": "drought",
    "description": "Crops wilted — no rain for 3 weeks",
    "estimated_loss_kes": 12000
  }'
```

**201 Created:**
```json
{
  "id": "CLM-20260702-001",
  "status": "UNDER_REVIEW",
  "loss_type": "drought",
  "policy_id": 123,
  "created_at": "2026-07-02T10:30:00Z",
  "message": "Claim submitted. Parametric evaluation will determine payout automatically."
}
```

---

### `GET /api/v1/claims/{id}/status/`
Get claim evaluation status.

```bash
curl -s http://localhost:8000/api/v1/claims/CLM-20260702-001/status/ \
  -H "Authorization: Bearer $TOKEN"
```

**200 OK:**
```json
{
  "claim_id": "CLM-20260702-001",
  "status": "APPROVED",
  "median_rainfall_mm": "14.50",
  "threshold_mm": "20.00",
  "payout_amount_kes": "15000.00",
  "payout_reference": "OFJ23456789",
  "payout_timestamp": "2026-07-02T23:05:42Z"
}
```

---

## 6. Payments Endpoints

### `POST /api/v1/payments/initiate/`
Initiate STK Push for premium payment.

```bash
curl -s -X POST http://localhost:8000/api/v1/payments/initiate/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "policy_id": 124,
    "phone": "254711234567",
    "amount": 1020.00
  }'
```

**200 OK:**
```json
{
  "checkout_request_id": "ws_CO_123456789",
  "merchant_request_id": "12345-67890",
  "response_code": "0",
  "customer_message": "Success. Request accepted for processing"
}
```

---

### `POST /api/v1/payments/mpesa/callback/`
M-Pesa Daraja callback endpoint (called by Safaricom servers).

```bash
# This is called by Safaricom — not by clients directly
# For testing, simulate a successful STK callback:
curl -s -X POST http://localhost:8000/api/v1/payments/mpesa/callback/ \
  -H 'Content-Type: application/json' \
  -d '{
    "Body": {
      "stkCallback": {
        "MerchantRequestID": "12345-67890",
        "CheckoutRequestID": "ws_CO_123456789",
        "ResultCode": 0,
        "ResultDesc": "The service request is processed successfully.",
        "CallbackMetadata": {
          "Item": [
            {"Name": "Amount", "Value": 1020.00},
            {"Name": "MpesaReceiptNumber", "Value": "OFJ23456789"},
            {"Name": "PhoneNumber", "Value": 254711234567}
          ]
        }
      }
    }
  }'
```

---

### `GET /api/v1/payments/payouts/`
List all parametric payouts for the farmer.

```bash
curl -s http://localhost:8000/api/v1/payments/payouts/ \
  -H "Authorization: Bearer $TOKEN"
```

**200 OK:**
```json
{
  "count": 1,
  "results": [
    {
      "id": "PAY-20260702-001",
      "policy_id": 123,
      "amount_kes": "15000.00",
      "mpesa_reference": "OFJ23456789",
      "trigger": "PARAMETRIC_DROUGHT",
      "status": "COMPLETED",
      "paid_at": "2026-07-02T23:05:42Z"
    }
  ]
}
```

---

## 7. Oracle Endpoints

### `POST /api/v1/oracles/submit-data/`
Submit signed satellite data (called by Oracle Node — requires oracle API key).

```bash
curl -s -X POST http://localhost:8000/api/v1/oracles/submit-data/ \
  -H 'Content-Type: application/json' \
  -H 'X-Oracle-Signature: 0xdeadbeef...' \
  -d '{
    "oracle_id": "oracle-1",
    "h3_index": "8928308280fffff",
    "timestamp": "2026-07-02T23:00:00Z",
    "rainfall_mm": 14.5,
    "ndvi": 0.62,
    "soil_moisture": 0.31,
    "data_sources": ["nasa-power", "chirps"]
  }'
```

**201 Created:**
```json
{
  "status": "received",
  "submission_id": "OBS-20260702-001",
  "h3_index": "8928308280fffff",
  "consensus_count": 2,
  "consensus_required": 3
}
```

---

### `GET /api/v1/oracles/`
List all registered oracle nodes (admin only).

```bash
curl -s http://localhost:8000/api/v1/oracles/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## 8. Geospatial Endpoints

### `GET /api/v1/geospatial/h3-index/?lat=-1.286&lng=36.817`
Get H3 cell for GPS coordinates.

```bash
curl -s "http://localhost:8000/api/v1/geospatial/h3-index/?lat=-1.286389&lng=36.817223&resolution=9"
```

**200 OK:**
```json
{
  "h3_index": "8928308280fffff",
  "resolution": 9,
  "center_lat": -1.2863,
  "center_lng": 36.8172,
  "area_km2": 0.105
}
```

---

### `POST /api/v1/geospatial/lookup/`
Lookup H3 cell info and active policy count.

```bash
curl -s -X POST http://localhost:8000/api/v1/geospatial/lookup/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"h3_index": "8928308280fffff"}'
```

**200 OK:**
```json
{
  "h3_index": "8928308280fffff",
  "active_policies": 47,
  "last_oracle_reading": "2026-07-02T23:00:00Z",
  "last_rainfall_mm": 14.5,
  "last_ndvi": 0.62
}
```

---

## 9. Pricing Endpoints

### `POST /api/v1/pricing/quote/`
Get a premium quote for a policy configuration.

```bash
curl -s -X POST http://localhost:8000/api/v1/pricing/quote/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "crop": "MAIZE",
    "acreage": 2.5,
    "ward_code": "WARD-KISUMU-01",
    "season": "LONG_RAINS_2026",
    "mitigation_techniques": ["drip_irrigation", "mulching"]
  }'
```

**200 OK:**
```json
{
  "base_premium_kes": 1200.00,
  "discount_percentage": 20.0,
  "discount_techniques": ["drip_irrigation", "mulching"],
  "final_premium_kes": 960.00,
  "payout_amount_kes": 15000.00,
  "threshold_mm": 20.0,
  "coverage_period": "2026-04-01 to 2026-09-30"
}
```

---

## 10. Satellite Data Endpoints

### `GET /api/v1/satellite/rainfall/?h3_index=8928308280fffff&days=30`
Get recent rainfall readings for an H3 cell.

```bash
curl -s "http://localhost:8000/api/v1/satellite/rainfall/?h3_index=8928308280fffff&days=30" \
  -H "Authorization: Bearer $TOKEN"
```

**200 OK:**
```json
{
  "h3_index": "8928308280fffff",
  "readings": [
    {"date": "2026-07-02", "rainfall_mm": 14.5, "source": "nasa-power"},
    {"date": "2026-07-01", "rainfall_mm": 8.2,  "source": "chirps"},
    {"date": "2026-06-30", "rainfall_mm": 21.1, "source": "nasa-power"}
  ],
  "30_day_average_mm": 12.8,
  "30_day_total_mm": 384.0
}
```

---

### `GET /api/v1/satellite/ndvi/?h3_index=8928308280fffff`
Get NDVI readings (vegetation index) for an H3 cell.

```bash
curl -s "http://localhost:8000/api/v1/satellite/ndvi/?h3_index=8928308280fffff" \
  -H "Authorization: Bearer $TOKEN"
```

---

### `POST /api/v1/satellite/trigger-evaluation/`
Manually trigger oracle evaluation for an H3 cell (admin only).

```bash
curl -s -X POST http://localhost:8000/api/v1/satellite/trigger-evaluation/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"h3_index": "8928308280fffff", "timestamp": "2026-07-02T23:00:00Z"}'
```

---

## 11. USSD Internal Endpoints

These endpoints are used internally by the USSD Microservice → Backend communication. They require the `X-Internal-API-Key` header.

### `POST /api/v1/ussd/internal/register/`

```bash
curl -s -X POST http://localhost:8000/api/v1/ussd/internal/register/ \
  -H 'Content-Type: application/json' \
  -H 'X-Internal-API-Key: bimagrid-internal-dev-key' \
  -d '{
    "phone": "254711234567",
    "ward_code": "WARD-KISUMU-01",
    "crop": "MAIZE",
    "acreage": "2.5",
    "mpesa_number": "254711234567"
  }'
```

**200 OK:**
```json
{
  "success": true,
  "policy_number": "POL-20260702-0003",
  "premium_kes": "1200.00",
  "message": "Policy created. Premium payment STK push sent to 254711234567."
}
```

---

### `GET /api/v1/ussd/internal/policy-status/?phone=254711234567`

```bash
curl -s "http://localhost:8000/api/v1/ussd/internal/policy-status/?phone=254711234567" \
  -H 'X-Internal-API-Key: bimagrid-internal-dev-key'
```

**200 OK:**
```json
{
  "status": "ACTIVE",
  "policy_number": "POL-20260702-0001",
  "crop": "MAIZE",
  "next_evaluation": "2026-07-03T23:00:00Z",
  "rainfall_this_week_mm": 42.3
}
```

---

## 12. Admin Dashboard Endpoints

### `GET /api/v1/admin/stats/`
Platform-wide statistics (admin only).

```bash
curl -s http://localhost:8000/api/v1/admin/stats/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**200 OK:**
```json
{
  "total_policies": 1247,
  "active_policies": 1103,
  "total_payouts": 89,
  "total_payout_amount_kes": 1335000.00,
  "total_premium_collected_kes": 1496400.00,
  "farmers_registered": 1247,
  "h3_cells_monitored": 34,
  "oracle_nodes_active": 3,
  "last_consensus_timestamp": "2026-07-02T23:05:00Z"
}
```

---

### `GET /api/v1/admin/payouts/`
List all payouts with farmer and policy details.

```bash
curl -s http://localhost:8000/api/v1/admin/payouts/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## 13. Health Endpoint

### `GET /health/`
Check service health (no auth required).

```bash
curl -s http://localhost:8000/health/
```

**200 OK:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "database": "ok",
  "redis": "ok",
  "timestamp": "2026-07-06T04:40:00Z"
}
```

```bash
# API Gateway health
curl -s http://localhost:3001/health
# {"status":"ok","version":"1.0.0","uptime":3600.5}

# USSD microservice health
curl -s http://localhost:8001/health/
```

---

## Common Error Responses

| Status | Body | Meaning |
|---|---|---|
| `400` | `{"field": ["error message"]}` | Validation error |
| `401` | `{"detail": "Authentication credentials were not provided."}` | Missing/invalid JWT |
| `403` | `{"detail": "You do not have permission to perform this action."}` | Insufficient permissions |
| `404` | `{"detail": "Not found."}` | Resource does not exist |
| `429` | `{"error": "Too Many Requests", "retryAfter": 60}` | Rate limit exceeded |
| `502` | `{"error": "Bad Gateway", "message": "Backend service unavailable"}` | Gateway proxy error |
| `500` | `{"detail": "Internal server error"}` | Unexpected server error |

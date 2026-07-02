# BimaGrid API Reference

> **Complete REST API documentation for all BimaGrid endpoints**

---

## Table of Contents

1. [Base URLs](#base-urls)
2. [Authentication](#authentication)
3. [Auth Endpoints](#auth-endpoints)
4. [Farmer Accounts](#farmer-accounts)
5. [Policies](#policies)
6. [Onboarding](#onboarding)
7. [Claims](#claims)
8. [Payments](#payments)
9. [Oracles](#oracles)
10. [Geospatial](#geospatial)
11. [Pricing](#pricing)
12. [Satellite](#satellite)
13. [USSD Internal](#ussd-internal)
14. [Admin Dashboard](#admin-dashboard)
15. [Health](#health)
16. [Error Reference](#error-reference)

---

## Base URLs

| Environment | Base URL |
|-------------|----------|
| **Production** | `https://api.bimagrid.io` |
| **Staging** | `https://staging-api.bimagrid.io` |
| **Development (Direct)** | `http://localhost:8000` |
| **Development (Via Gateway)** | `http://localhost:3001/api` |

All endpoints below use `http://localhost:8000` as the base URL unless otherwise noted.

---

## Authentication

BimaGrid uses **JWT Bearer Token** authentication via Django SimpleJWT.

- **Access tokens** expire after **15 minutes**
- **Refresh tokens** expire after **7 days**
- Include the access token in the `Authorization` header for all protected endpoints

```
Authorization: Bearer <access_token>
```

### Obtain Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "farmer@example.com", "password": "yourpassword"}'
```

**Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Store both tokens. Use `access` for API calls; use `refresh` to get a new `access` token when it expires.

---

## Auth Endpoints

### POST /api/v1/auth/token/

Obtain a JWT access + refresh token pair.

**Headers:** `Content-Type: application/json`

**Request Body:**
```json
{
  "username": "farmer@example.com",
  "password": "yourpassword"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "farmer@example.com",
    "password": "yourpassword"
  }'
```

**Response `200 OK`:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MTcyMDkwMDB9.abc123",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE3MTc4MDAwMDB9.xyz789"
}
```

**Errors:**
| Code | Description |
|------|-------------|
| `400` | Missing username or password |
| `401` | Invalid credentials |

---

### POST /api/v1/auth/refresh/

Exchange a refresh token for a new access token.

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh/ \
  -H 'Content-Type: application/json' \
  -d '{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response `200 OK`:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.new-access-token..."
}
```

**Errors:**
| Code | Description |
|------|-------------|
| `401` | Token is invalid or expired |

---

### POST /api/v1/auth/register/

Register a new user account (web portal users).

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "admin@bimagrid.io",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "Alice",
    "last_name": "Wanjiku",
    "role": "admin"
  }'
```

**Response `201 Created`:**
```json
{
  "id": "usr_01J2K3L4M5N6O7P8Q9R0",
  "email": "admin@bimagrid.io",
  "first_name": "Alice",
  "last_name": "Wanjiku",
  "role": "admin",
  "created_at": "2024-06-01T10:00:00Z"
}
```

**Errors:**
| Code | Description |
|------|-------------|
| `400` | Validation error (passwords don't match, weak password) |
| `409` | Email already registered |

---

## Farmer Accounts

### GET /api/v1/accounts/me/

Get the authenticated user's account details.

**Headers:** `Authorization: Bearer <token>`

**cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/accounts/me/ \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
```

**Response `200 OK`:**
```json
{
  "id": "usr_01J2K3L4M5N6O7P8Q9R0",
  "email": "farmer@example.com",
  "phone": "+254712345678",
  "national_id": "12345678",
  "first_name": "John",
  "last_name": "Kamau",
  "role": "farmer",
  "farmer_profile": {
    "farm_name": "Kamau Farm",
    "h3_cell_index": "8928308280fffff",
    "gps_lat": -0.0236,
    "gps_lng": 37.9062,
    "farm_area_ha": 1.5,
    "primary_crop": "maize",
    "county": "Meru",
    "sub_county": "Imenti North"
  },
  "kyc_status": "verified",
  "created_at": "2024-03-15T08:30:00Z",
  "updated_at": "2024-05-20T14:22:00Z"
}
```

---

### PATCH /api/v1/accounts/me/

Update the authenticated user's account details.

**cURL:**
```bash
curl -X PATCH http://localhost:8000/api/v1/accounts/me/ \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "first_name": "John",
    "last_name": "Mwangi",
    "farmer_profile": {
      "primary_crop": "beans",
      "farm_area_ha": 2.0
    }
  }'
```

**Response `200 OK`:** Returns updated account object (same schema as GET /me/).

---

### GET /api/v1/accounts/profile/

Get extended farmer profile including policy summary.

**cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/accounts/profile/ \
  -H 'Authorization: Bearer <token>'
```

**Response `200 OK`:**
```json
{
  "farmer_id": "fmr_01J2K3L4M5N6O7P8Q9R0",
  "display_name": "John Kamau",
  "phone": "+254712345678",
  "h3_cell_index": "8928308280fffff",
  "location_display": "Imenti North, Meru County",
  "active_policies": 2,
  "total_coverage_kes": 25000,
  "total_claims_paid_kes": 5200,
  "member_since": "2024-03-15",
  "last_premium_paid": "2024-04-01T09:00:00Z"
}
```

---

## Policies

### GET /api/v1/policies/

List all policies for the authenticated farmer.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status: `active`, `expired`, `claimed`, `pending` |
| `page` | int | Page number (default: 1) |
| `page_size` | int | Items per page (default: 20, max: 100) |

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/policies/?status=active&page=1" \
  -H 'Authorization: Bearer <token>'
```

**Response `200 OK`:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "pol_01J2K3L4M5N6O7P8Q9R0",
      "policy_number": "BG-2024-KE-0042",
      "farmer_id": "fmr_01J2K3L4M5N6O7P8Q9R0",
      "h3_cell_index": "8928308280fffff",
      "trigger_type": "drought",
      "trigger_threshold_mm": 40.0,
      "coverage_amount_kes": 12500,
      "premium_paid_kes": 450,
      "status": "active",
      "season_start": "2024-03-01",
      "season_end": "2024-09-30",
      "on_chain_policy_id": "0x1a2b3c4d...",
      "created_at": "2024-03-01T10:00:00Z"
    }
  ]
}
```

---

### POST /api/v1/policies/

Create a new insurance policy.

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/policies/ \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "trigger_type": "drought",
    "coverage_amount_kes": 12500,
    "season_start": "2024-03-01",
    "season_end": "2024-09-30",
    "crop_type": "maize",
    "trigger_threshold_mm": 40.0,
    "trigger_window_days": 30
  }'
```

**Response `201 Created`:**
```json
{
  "id": "pol_01J2K3L4M5N6O7P8Q9R0",
  "policy_number": "BG-2024-KE-0042",
  "status": "pending_payment",
  "premium_amount_kes": 450,
  "mpesa_stk_push_initiated": true,
  "payment_reference": "pay_01J2K3L4M5N6O7P8Q9R0",
  "message": "STK Push sent to +254712345678. Confirm payment to activate policy."
}
```

---

### GET /api/v1/policies/{id}/

Get details of a specific policy.

**cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/policies/pol_01J2K3L4M5N6O7P8Q9R0/ \
  -H 'Authorization: Bearer <token>'
```

**Response `200 OK`:**
```json
{
  "id": "pol_01J2K3L4M5N6O7P8Q9R0",
  "policy_number": "BG-2024-KE-0042",
  "farmer": {
    "id": "fmr_01J2K3L4M5N6O7P8Q9R0",
    "name": "John Kamau",
    "phone": "+254712345678"
  },
  "h3_cell_index": "8928308280fffff",
  "location_display": "Imenti North, Meru County",
  "trigger_type": "drought",
  "trigger_threshold_mm": 40.0,
  "trigger_window_days": 30,
  "coverage_amount_kes": 12500,
  "premium_paid_kes": 450,
  "status": "active",
  "season_start": "2024-03-01",
  "season_end": "2024-09-30",
  "on_chain_policy_id": "0x1a2b3c4d5e6f7890",
  "escrow_vault_address": "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0",
  "last_oracle_reading": {
    "rainfall_mm_30d": 52.3,
    "ndvi_score": 0.61,
    "reading_timestamp": "2024-06-15T06:00:00Z"
  },
  "claims": [],
  "created_at": "2024-03-01T10:00:00Z",
  "updated_at": "2024-06-15T06:01:00Z"
}
```

**Errors:**
| Code | Description |
|------|-------------|
| `404` | Policy not found |
| `403` | Policy belongs to another farmer |

---

### PATCH /api/v1/policies/{id}/

Update a policy (limited fields while active).

**cURL:**
```bash
curl -X PATCH http://localhost:8000/api/v1/policies/pol_01J2K3L4M5N6O7P8Q9R0/ \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "beneficiary_phone": "+254798765432"
  }'
```

**Response `200 OK`:** Returns updated policy object.

---

### GET /api/v1/policies/{id}/status/

Get a concise policy status summary (optimized for USSD display).

**cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/policies/pol_01J2K3L4M5N6O7P8Q9R0/status/ \
  -H 'Authorization: Bearer <token>'
```

**Response `200 OK`:**
```json
{
  "policy_number": "BG-2024-KE-0042",
  "status": "active",
  "days_remaining": 107,
  "coverage_kes": 12500,
  "current_rainfall_30d_mm": 52.3,
  "threshold_mm": 40.0,
  "risk_level": "normal",
  "last_checked": "2024-06-15T06:00:00Z"
}
```

---

## Onboarding

### POST /api/v1/onboarding/register-farmer/

Register a new farmer (extended KYC registration, typically called from web portal).

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/onboarding/register-farmer/ \
  -H 'Content-Type: application/json' \
  -d '{
    "phone": "+254712345678",
    "national_id": "12345678",
    "first_name": "John",
    "last_name": "Kamau",
    "date_of_birth": "1985-04-15",
    "gps_lat": -0.0236,
    "gps_lng": 37.9062,
    "farm_area_ha": 1.5,
    "primary_crop": "maize",
    "county": "Meru",
    "sub_county": "Imenti North",
    "email": "john.kamau@example.com"
  }'
```

**Response `201 Created`:**
```json
{
  "farmer_id": "fmr_01J2K3L4M5N6O7P8Q9R0",
  "phone": "+254712345678",
  "h3_cell_index": "8928308280fffff",
  "kyc_status": "pending_verification",
  "verification_method": "national_id",
  "onboarding_token": "onb_01J2K3L4M5N6O7P8Q9R0",
  "next_step": "verify_identity",
  "message": "OTP sent to +254712345678 for identity verification."
}
```

---

### POST /api/v1/onboarding/verify-identity/

Verify farmer identity using OTP sent to their phone.

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/onboarding/verify-identity/ \
  -H 'Content-Type: application/json' \
  -d '{
    "onboarding_token": "onb_01J2K3L4M5N6O7P8Q9R0",
    "otp_code": "847291",
    "national_id": "12345678"
  }'
```

**Response `200 OK`:**
```json
{
  "farmer_id": "fmr_01J2K3L4M5N6O7P8Q9R0",
  "kyc_status": "verified",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "Identity verified. Welcome to BimaGrid!"
}
```

---

### GET /api/v1/onboarding/status/

Check onboarding completion status.

**cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/onboarding/status/ \
  -H 'Authorization: Bearer <token>'
```

**Response `200 OK`:**
```json
{
  "farmer_id": "fmr_01J2K3L4M5N6O7P8Q9R0",
  "onboarding_complete": true,
  "steps": {
    "registration": "complete",
    "identity_verification": "complete",
    "farm_geolocation": "complete",
    "first_policy": "complete"
  },
  "kyc_status": "verified",
  "eligible_for_policy": true
}
```

---

## Claims

### GET /api/v1/claims/

List all claims for the authenticated farmer.

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/claims/?status=approved" \
  -H 'Authorization: Bearer <token>'
```

**Response `200 OK`:**
```json
{
  "count": 1,
  "results": [
    {
      "id": "clm_01J2K3L4M5N6O7P8Q9R0",
      "policy_id": "pol_01J2K3L4M5N6O7P8Q9R0",
      "policy_number": "BG-2024-KE-0042",
      "claim_type": "automated",
      "trigger_type": "drought",
      "incident_date": "2024-05-31",
      "status": "approved",
      "trigger_data": {
        "rainfall_30d_mm": 28.4,
        "threshold_mm": 40.0,
        "deficit_mm": 11.6,
        "oracle_tx_hash": "0xabc123..."
      },
      "payout_amount_kes": 5200,
      "payout_status": "disbursed",
      "mpesa_reference": "QWE123ABC",
      "created_at": "2024-06-01T04:12:00Z",
      "resolved_at": "2024-06-01T04:14:30Z"
    }
  ]
}
```

---

### POST /api/v1/claims/

Submit a manual claim (supplements automated oracle-triggered claims).

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/claims/ \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "policy_id": "pol_01J2K3L4M5N6O7P8Q9R0",
    "incident_type": "drought",
    "incident_date": "2024-05-31",
    "estimated_loss_percentage": 60,
    "notes": "Crops wilting, no rainfall since early May",
    "evidence_description": "Visible crop damage in northern section of farm"
  }'
```

**Response `201 Created`:**
```json
{
  "id": "clm_01J2K3L4M5N6O7P8Q9R0",
  "status": "pending_oracle_verification",
  "message": "Claim submitted. Oracle data will be evaluated within 6 hours.",
  "expected_resolution": "2024-06-01T12:00:00Z"
}
```

---

### GET /api/v1/claims/{id}/

Get details of a specific claim.

**cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/claims/clm_01J2K3L4M5N6O7P8Q9R0/ \
  -H 'Authorization: Bearer <token>'
```

**Response `200 OK`:** Returns full claim object (see GET /claims/ for schema).

---

### GET /api/v1/claims/{id}/status/

Get concise claim status (optimized for USSD/SMS).

**cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/claims/clm_01J2K3L4M5N6O7P8Q9R0/status/ \
  -H 'Authorization: Bearer <token>'
```

**Response `200 OK`:**
```json
{
  "claim_id": "clm_01J2K3L4M5N6O7P8Q9R0",
  "status": "approved",
  "payout_amount_kes": 5200,
  "mpesa_reference": "QWE123ABC",
  "message": "Claim approved. KES 5,200 sent to +254712345678."
}
```

---

## Payments

### POST /api/v1/payments/initiate/

Initiate a premium payment via M-Pesa STK Push.

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/payments/initiate/ \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "policy_id": "pol_01J2K3L4M5N6O7P8Q9R0",
    "amount_kes": 450,
    "phone": "+254712345678",
    "payment_type": "premium"
  }'
```

**Response `202 Accepted`:**
```json
{
  "payment_id": "pay_01J2K3L4M5N6O7P8Q9R0",
  "mpesa_checkout_request_id": "ws_CO_20240601_123456789",
  "status": "pending",
  "message": "STK Push sent to +254712345678. Enter your M-Pesa PIN to confirm.",
  "expires_at": "2024-06-01T10:05:00Z"
}
```

---

### GET /api/v1/payments/{id}/

Get payment details and status.

**cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/payments/pay_01J2K3L4M5N6O7P8Q9R0/ \
  -H 'Authorization: Bearer <token>'
```

**Response `200 OK`:**
```json
{
  "id": "pay_01J2K3L4M5N6O7P8Q9R0",
  "policy_id": "pol_01J2K3L4M5N6O7P8Q9R0",
  "amount_kes": 450,
  "payment_type": "premium",
  "status": "completed",
  "mpesa_receipt_number": "QWE123ABC456",
  "phone": "+254712345678",
  "transaction_date": "2024-06-01T10:02:30Z",
  "created_at": "2024-06-01T10:00:00Z"
}
```

---

### POST /api/v1/payments/mpesa/callback/

**Internal endpoint** — M-Pesa Daraja STK Push callback. Called by Safaricom servers.

> ⚠️ This endpoint is called by M-Pesa servers, not by clients directly. Ensure your `MPESA_CALLBACK_URL` is set to this endpoint's public URL.

**cURL (simulating M-Pesa callback for testing):**
```bash
curl -X POST http://localhost:8000/api/v1/payments/mpesa/callback/ \
  -H 'Content-Type: application/json' \
  -d '{
    "Body": {
      "stkCallback": {
        "MerchantRequestID": "29115-34620561-1",
        "CheckoutRequestID": "ws_CO_20240601_123456789",
        "ResultCode": 0,
        "ResultDesc": "The service request is processed successfully.",
        "CallbackMetadata": {
          "Item": [
            {"Name": "Amount", "Value": 450},
            {"Name": "MpesaReceiptNumber", "Value": "QWE123ABC456"},
            {"Name": "TransactionDate", "Value": 20240601100230},
            {"Name": "PhoneNumber", "Value": 254712345678}
          ]
        }
      }
    }
  }'
```

**Response `200 OK`:**
```json
{"ResultCode": 0, "ResultDesc": "Accepted"}
```

---

### GET /api/v1/payments/payouts/

List all payout disbursements (claims paid out to farmers).

**Query Parameters:** `status`, `from_date`, `to_date`, `page`

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/payments/payouts/?status=disbursed" \
  -H 'Authorization: Bearer <token>'
```

**Response `200 OK`:**
```json
{
  "count": 3,
  "results": [
    {
      "id": "pyt_01J2K3L4M5N6O7P8Q9R0",
      "claim_id": "clm_01J2K3L4M5N6O7P8Q9R0",
      "policy_number": "BG-2024-KE-0042",
      "farmer_phone": "+254712345678",
      "amount_kes": 5200,
      "mpesa_reference": "QWE123ABC",
      "status": "disbursed",
      "disbursed_at": "2024-06-01T04:14:30Z"
    }
  ]
}
```

---

## Oracles

### POST /api/v1/oracles/submit-data/

Submit oracle weather data reading (typically called by the Oracle Node via gRPC; REST fallback available).

**Headers:** `Authorization: Bearer <oracle-service-token>`, `Content-Type: application/json`

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/oracles/submit-data/ \
  -H 'Authorization: Bearer <oracle-service-token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "h3_cells": ["8928308280fffff", "8928308281fffff"],
    "rainfall_mm": 38.5,
    "ndvi_score": 0.42,
    "evapotranspiration": 5.2,
    "timestamp": "2024-06-15T06:00:00Z",
    "data_source": "chirps_v2",
    "signature": "0x304402201a2b3c...",
    "oracle_pubkey": "02abcdef1234567890..."
  }'
```

**Response `201 Created`:**
```json
{
  "submission_id": "ors_01J2K3L4M5N6O7P8Q9R0",
  "accepted_cells": ["8928308280fffff", "8928308281fffff"],
  "rejected_cells": [],
  "thresholds_breached": [],
  "on_chain_tx_hash": "0xabc123def456...",
  "timestamp": "2024-06-15T06:00:00Z"
}
```

---

### GET /api/v1/oracles/

List oracle submissions (admin only).

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/oracles/?h3_cell=8928308280fffff&limit=10" \
  -H 'Authorization: Bearer <admin-token>'
```

**Response `200 OK`:**
```json
{
  "count": 120,
  "results": [
    {
      "id": "ors_01J2K3L4M5N6O7P8Q9R0",
      "h3_cell": "8928308280fffff",
      "rainfall_mm": 38.5,
      "ndvi_score": 0.42,
      "evapotranspiration": 5.2,
      "data_source": "chirps_v2",
      "oracle_pubkey": "02abcdef...",
      "signature_valid": true,
      "on_chain_tx_hash": "0xabc123...",
      "threshold_breached": false,
      "reading_timestamp": "2024-06-15T06:00:00Z",
      "created_at": "2024-06-15T06:01:00Z"
    }
  ]
}
```

---

### GET /api/v1/oracles/{id}/

Get a specific oracle submission.

**cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/oracles/ors_01J2K3L4M5N6O7P8Q9R0/ \
  -H 'Authorization: Bearer <admin-token>'
```

**Response `200 OK`:** Returns full oracle submission object (see GET /oracles/ for schema).

---

## Geospatial

### GET /api/v1/geospatial/h3-index/

Convert GPS coordinates to H3 cell index at resolution 9.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lat` | float | ✅ | Latitude in decimal degrees |
| `lng` | float | ✅ | Longitude in decimal degrees |
| `resolution` | int | ❌ | H3 resolution (default: 9) |

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/geospatial/h3-index/?lat=-0.0236&lng=37.9062" \
  -H 'Authorization: Bearer <token>'
```

**Response `200 OK`:**
```json
{
  "lat": -0.0236,
  "lng": 37.9062,
  "resolution": 9,
  "h3_index": "8928308280fffff",
  "h3_index_bytes32": "0x0000000000000000000000000000000000000000000000008928308280fffff",
  "cell_center_lat": -0.0241,
  "cell_center_lng": 37.9058,
  "cell_area_km2": 0.105,
  "county": "Meru",
  "country": "Kenya"
}
```

---

### GET /api/v1/geospatial/coverage/

Get all H3 cells with active BimaGrid coverage.

**Query Parameters:** `country` (ISO 3166-1 alpha-2), `county`

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/geospatial/coverage/?country=KE" \
  -H 'Authorization: Bearer <token>'
```

**Response `200 OK`:**
```json
{
  "country": "KE",
  "total_cells": 4832,
  "active_policy_cells": 1247,
  "cells": [
    {
      "h3_index": "8928308280fffff",
      "active_policies": 12,
      "total_coverage_kes": 150000,
      "risk_level": "medium",
      "last_oracle_reading": "2024-06-15T06:00:00Z"
    }
  ]
}
```

---

### POST /api/v1/geospatial/lookup/

Look up policy and risk information for a GPS location.

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/geospatial/lookup/ \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "lat": -0.0236,
    "lng": 37.9062
  }'
```

**Response `200 OK`:**
```json
{
  "h3_index": "8928308280fffff",
  "location": "Imenti North, Meru County, Kenya",
  "coverage_available": true,
  "risk_profile": {
    "drought_risk": "medium",
    "flood_risk": "low",
    "historical_drought_frequency_per_decade": 2.3
  },
  "available_products": [
    {
      "trigger_type": "drought",
      "coverage_range_kes": {"min": 5000, "max": 50000},
      "estimated_premium_rate": 0.036
    }
  ],
  "current_conditions": {
    "rainfall_30d_mm": 52.3,
    "ndvi_score": 0.61,
    "last_updated": "2024-06-15T06:00:00Z"
  }
}
```

---

## Pricing

### POST /api/v1/pricing/quote/

Generate a premium quote for a prospective policy.

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/pricing/quote/ \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "h3_cell_index": "8928308280fffff",
    "trigger_type": "drought",
    "coverage_amount_kes": 12500,
    "season_start": "2024-03-01",
    "season_end": "2024-09-30",
    "crop_type": "maize",
    "trigger_threshold_mm": 40.0,
    "trigger_window_days": 30
  }'
```

**Response `200 OK`:**
```json
{
  "quote_id": "qte_01J2K3L4M5N6O7P8Q9R0",
  "coverage_amount_kes": 12500,
  "premium_amount_kes": 450,
  "premium_rate": 0.036,
  "risk_score": 0.42,
  "trigger_type": "drought",
  "trigger_threshold_mm": 40.0,
  "trigger_window_days": 30,
  "season_days": 214,
  "pricing_factors": {
    "base_rate": 0.030,
    "drought_risk_adjustment": 0.004,
    "crop_type_adjustment": 0.002,
    "h3_zone_adjustment": 0.000
  },
  "valid_until": "2024-06-02T10:00:00Z"
}
```

---

### GET /api/v1/pricing/rules/

Get active pricing rules and rate tables (admin/actuarial).

**cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/pricing/rules/ \
  -H 'Authorization: Bearer <admin-token>'
```

**Response `200 OK`:**
```json
{
  "rules": [
    {
      "id": "prl_01",
      "trigger_type": "drought",
      "base_rate": 0.030,
      "risk_multipliers": {
        "low": 0.8,
        "medium": 1.0,
        "high": 1.5,
        "very_high": 2.0
      },
      "crop_adjustments": {
        "maize": 0.002,
        "beans": 0.003,
        "coffee": -0.001
      },
      "min_coverage_kes": 2000,
      "max_coverage_kes": 100000,
      "effective_from": "2024-01-01",
      "effective_to": null
    }
  ]
}
```

---

## Satellite

### GET /api/v1/satellite/ndvi/

Get NDVI (Normalized Difference Vegetation Index) readings for an H3 cell.

**Query Parameters:** `h3_cell` (required), `from_date`, `to_date`

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/satellite/ndvi/?h3_cell=8928308280fffff&from_date=2024-04-01&to_date=2024-06-15" \
  -H 'Authorization: Bearer <token>'
```

**Response `200 OK`:**
```json
{
  "h3_cell": "8928308280fffff",
  "data_source": "openeo_sentinel2",
  "readings": [
    {
      "date": "2024-04-01",
      "ndvi_score": 0.72,
      "cloud_cover_pct": 5.2
    },
    {
      "date": "2024-05-01",
      "ndvi_score": 0.61,
      "cloud_cover_pct": 12.1
    },
    {
      "date": "2024-06-01",
      "ndvi_score": 0.45,
      "cloud_cover_pct": 8.3
    }
  ],
  "trend": "declining",
  "anomaly_detected": true
}
```

---

### GET /api/v1/satellite/rainfall/

Get CHIRPS rainfall accumulation data for an H3 cell.

**Query Parameters:** `h3_cell` (required), `window_days` (default: 30), `end_date`

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/satellite/rainfall/?h3_cell=8928308280fffff&window_days=30" \
  -H 'Authorization: Bearer <token>'
```

**Response `200 OK`:**
```json
{
  "h3_cell": "8928308280fffff",
  "data_source": "chirps_v2",
  "window_days": 30,
  "end_date": "2024-06-15",
  "total_rainfall_mm": 38.5,
  "daily_readings": [
    {"date": "2024-05-16", "rainfall_mm": 0.0},
    {"date": "2024-05-17", "rainfall_mm": 2.3},
    {"date": "2024-05-18", "rainfall_mm": 8.1}
  ],
  "long_term_average_mm": 68.2,
  "anomaly_pct": -43.6,
  "drought_threshold_mm": 40.0,
  "below_threshold": true
}
```

---

### POST /api/v1/satellite/trigger-evaluation/

Manually trigger satellite data evaluation for a set of H3 cells (admin only).

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/satellite/trigger-evaluation/ \
  -H 'Authorization: Bearer <admin-token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "h3_cells": ["8928308280fffff", "8928308281fffff"],
    "evaluation_date": "2024-06-15",
    "force_oracle_submit": true
  }'
```

**Response `202 Accepted`:**
```json
{
  "task_id": "tsk_01J2K3L4M5N6O7P8Q9R0",
  "status": "queued",
  "cells_queued": 2,
  "message": "Evaluation task queued. Results will be submitted to oracle within 10 minutes."
}
```

---

## USSD Internal

These endpoints are called by the USSD Microservice (via gRPC in production; REST available for debugging).

### POST /api/v1/ussd/internal/register/

Register a farmer from a USSD session.

**Headers:** `X-USSD-Service-Key: <internal-service-key>`

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/ussd/internal/register/ \
  -H 'X-USSD-Service-Key: ussd-internal-secret' \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "ATSession123",
    "phone": "+254712345678",
    "national_id": "12345678",
    "name": "John Kamau",
    "gps_lat": -0.0236,
    "gps_lng": 37.9062,
    "crop_type": "maize",
    "farm_area_ha": 1.5
  }'
```

**Response `201 Created`:**
```json
{
  "farmer_id": "fmr_01J2K3L4M5N6O7P8Q9R0",
  "h3_cell_index": "8928308280fffff",
  "ussd_message": "Registration successful! Your farmer ID: BG-KE-042. Dial *384# to purchase a policy.",
  "registration_complete": true
}
```

---

### GET /api/v1/ussd/internal/policy-status/

Get policy status for a farmer by phone number (USSD session lookup).

**Query Parameters:** `phone` (required)

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/ussd/internal/policy-status/?phone=%2B254712345678" \
  -H 'X-USSD-Service-Key: ussd-internal-secret'
```

**Response `200 OK`:**
```json
{
  "farmer_name": "John Kamau",
  "has_active_policy": true,
  "policies": [
    {
      "policy_number": "BG-2024-KE-0042",
      "status": "active",
      "coverage_kes": 12500,
      "days_remaining": 107,
      "ussd_summary": "Policy BG-0042: Active. KES 12,500 cover. 107 days left."
    }
  ]
}
```

---

### POST /api/v1/ussd/internal/claim/

Initiate a claim from a USSD session.

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/ussd/internal/claim/ \
  -H 'X-USSD-Service-Key: ussd-internal-secret' \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "ATSession123",
    "phone": "+254712345678",
    "policy_id": "pol_01J2K3L4M5N6O7P8Q9R0",
    "incident_type": "drought",
    "incident_date": "2024-05-31"
  }'
```

**Response `201 Created`:**
```json
{
  "claim_id": "clm_01J2K3L4M5N6O7P8Q9R0",
  "ussd_message": "Claim BG-CLM-001 submitted. We will evaluate your claim within 6 hours and send you an SMS update.",
  "status": "pending"
}
```

---

## Admin Dashboard

### GET /api/v1/admin/stats/

Get protocol-wide statistics (admin only).

**cURL:**
```bash
curl -X GET http://localhost:8000/api/v1/admin/stats/ \
  -H 'Authorization: Bearer <admin-token>'
```

**Response `200 OK`:**
```json
{
  "as_of": "2024-06-15T12:00:00Z",
  "farmers": {
    "total_registered": 8432,
    "kyc_verified": 7891,
    "with_active_policy": 5234
  },
  "policies": {
    "total": 6102,
    "active": 5234,
    "expired": 712,
    "claimed": 156,
    "total_coverage_kes": 78540000,
    "total_premiums_collected_kes": 2827440
  },
  "claims": {
    "total": 234,
    "approved": 156,
    "pending": 42,
    "rejected": 36,
    "total_paid_out_kes": 812000
  },
  "oracle": {
    "active_cells": 1247,
    "last_submission": "2024-06-15T06:01:00Z",
    "submissions_last_24h": 4988
  },
  "blockchain": {
    "escrow_balance_celo": 14233.72,
    "network": "Celo Mainnet",
    "chain_id": 42220
  }
}
```

---

### GET /api/v1/admin/policies/

List all policies across all farmers (admin only).

**Query Parameters:** `status`, `county`, `h3_cell`, `from_date`, `to_date`, `page`, `page_size`

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/admin/policies/?county=Meru&status=active&page=1" \
  -H 'Authorization: Bearer <admin-token>'
```

**Response `200 OK`:**
```json
{
  "count": 312,
  "next": "http://localhost:8000/api/v1/admin/policies/?county=Meru&status=active&page=2",
  "previous": null,
  "results": [
    {
      "id": "pol_01J2K3L4M5N6O7P8Q9R0",
      "policy_number": "BG-2024-KE-0042",
      "farmer_name": "John Kamau",
      "farmer_phone": "+254712345678",
      "county": "Meru",
      "h3_cell": "8928308280fffff",
      "coverage_kes": 12500,
      "premium_kes": 450,
      "status": "active",
      "season_end": "2024-09-30",
      "current_rainfall_30d_mm": 52.3
    }
  ]
}
```

---

### GET /api/v1/admin/payouts/

List all payout disbursements (admin only).

**Query Parameters:** `status`, `from_date`, `to_date`, `county`, `page`

**cURL:**
```bash
curl -X GET "http://localhost:8000/api/v1/admin/payouts/?from_date=2024-06-01&to_date=2024-06-30" \
  -H 'Authorization: Bearer <admin-token>'
```

**Response `200 OK`:**
```json
{
  "count": 23,
  "total_disbursed_kes": 119600,
  "results": [
    {
      "id": "pyt_01J2K3L4M5N6O7P8Q9R0",
      "policy_number": "BG-2024-KE-0042",
      "farmer_name": "John Kamau",
      "farmer_phone": "+254712345678",
      "county": "Meru",
      "claim_type": "automated",
      "trigger_type": "drought",
      "amount_kes": 5200,
      "mpesa_reference": "QWE123ABC",
      "status": "disbursed",
      "disbursed_at": "2024-06-01T04:14:30Z"
    }
  ]
}
```

---

## Health

### GET /health/

Service health check endpoint.

**cURL:**
```bash
curl -X GET http://localhost:8000/health/
```

**Response `200 OK`:**
```json
{
  "status": "healthy",
  "version": "1.4.2",
  "timestamp": "2024-06-15T12:00:00Z",
  "services": {
    "database": "connected",
    "redis": "connected",
    "celery": "connected",
    "grpc": "listening",
    "oracle_last_heartbeat": "2024-06-15T11:58:00Z"
  },
  "uptime_seconds": 86400
}
```

**Response `503 Service Unavailable`** (when degraded):
```json
{
  "status": "degraded",
  "services": {
    "database": "connected",
    "redis": "disconnected",
    "celery": "unknown"
  }
}
```

---

## Error Reference

All error responses follow a consistent JSON structure:

```json
{
  "error": "error_code",
  "message": "Human-readable description of the error",
  "details": {},
  "request_id": "req_01J2K3L4M5N6O7P8Q9R0"
}
```

### Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|-----------|-------------|
| `400` | `validation_error` | Request body failed validation |
| `400` | `invalid_h3_index` | Provided H3 cell index is malformed |
| `401` | `authentication_required` | No or invalid JWT token provided |
| `401` | `token_expired` | JWT access token has expired — refresh it |
| `403` | `permission_denied` | Authenticated user lacks required role |
| `403` | `policy_not_owned` | Policy belongs to a different farmer |
| `404` | `not_found` | Resource does not exist |
| `409` | `duplicate_policy` | Farmer already has an active policy for this season and H3 cell |
| `409` | `duplicate_claim` | An active claim already exists for this policy |
| `422` | `coverage_area_unavailable` | No BimaGrid coverage for the given GPS location |
| `422` | `below_minimum_coverage` | Coverage amount below minimum KES 2,000 |
| `429` | `rate_limit_exceeded` | Too many requests — slow down |
| `500` | `internal_server_error` | Unexpected server error |
| `502` | `oracle_unavailable` | Oracle node is not responding |
| `503` | `blockchain_unavailable` | Blockchain RPC endpoint unreachable |

### Example Error Response

```json
{
  "error": "validation_error",
  "message": "Request body contains invalid data.",
  "details": {
    "coverage_amount_kes": ["Ensure this value is greater than or equal to 2000."],
    "season_end": ["Season end date must be after season start date."]
  },
  "request_id": "req_01J2K3L4M5N6O7P8Q9R0"
}
```

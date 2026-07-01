# BimaGrid External APIs & Protocols Documentation

## Document Metadata

| Field | Value |
| --- | --- |
| Document Version | 1.0.0 |
| Last Updated | July 1, 2026 |
| Maintainer | BimaGrid Engineering Team |

## Table of Contents

1. Overview
2. Telecommunication APIs
3. Payment APIs
4. Government Integration APIs
5. Weather & Climate Data APIs
6. Satellite & Earth Observation APIs
7. Blockchain Protocols
8. Authentication Protocols
9. Data Exchange Protocols
10. Webhook Protocols
11. API Security Standards
12. Rate Limiting Policies
13. Error Handling Standards
14. API Versioning Strategy
15. Monitoring & Observability
16. API Testing Strategy
17. Compliance & Regulatory APIs
18. Third-Party Service APIs
19. API Documentation Standards
20. API Lifecycle Management

## 1. Overview

BimaGrid integrates with numerous external APIs and protocols to deliver its parametric insurance service. This document provides comprehensive documentation of all external integrations, their protocols, authentication mechanisms, rate limits, and usage patterns.

### Integration Categories

- Telecommunication (USSD, SMS, Voice)
- Payment Processing (M-Pesa, Mobile Money)
- Government Services (Identity, Land Registry)
- Weather & Climate Data (CHIRPS, NASA POWER, etc.)
- Satellite & Earth Observation (Sentinel, openEO)
- Blockchain (Custom Rust chain, Ethereum JSON-RPC)
- Authentication (OAuth 2.0, OIDC, API Keys)

### Design Principles

1. Resilience: Circuit breakers, retries, fallbacks
2. Security: Encryption, authentication, authorization
3. Performance: Caching, batching, async processing
4. Monitoring: Logging, metrics, alerting
5. Compliance: Data protection, audit trails

## 2. Telecommunication APIs

### 2.1 Africa's Talking API

Provider: Africa's Talking

Base URL: https://api.africastalking.com/version1/

Documentation: https://build.at-labs.io/docs

Purpose:

- USSD gateway for farmer interactions
- SMS gateway for notifications and alerts
- Voice API for IVR (future)

Authentication:

- Method: API Key in header
- Header: apiKey: YOUR_API_KEY
- Username: YOUR_USERNAME

#### USSD API

Endpoint: `POST /userdata`

Base URL: https://api.africastalking.com/version1/

Request headers:

- Content-Type: application/x-www-form-urlencoded
- apiKey: YOUR_API_KEY
- Accept: application/json

Request parameters:

- username: string (required) - Your Africa's Talking username
- sessionId: string (required) - Unique session identifier
- phoneNumber: string (required) - User's phone number (E.164 format)
- text: string (required) - Cumulative session input (delimited by *)
- serviceCode: string (required) - Your USSD service code

Request example:

```http
POST /userdata HTTP/1.1
Host: api.africastalking.com
Content-Type: application/x-www-form-urlencoded
apiKey: atksk_XXXXXXXXXXXXXXXXXXXX

username=myUsername&sessionId=ATUid_123456789&phoneNumber=254712345678&text=1*1234*1*2
```

Response format:

- Content-Type: text/plain
- Prefix: CON (continue) or END (terminate)

Response example (Continue):

```text
CON Enter your 4-digit Ward Code:
```

Response example (Terminate):

```text
END Registration complete. Premium: KES 250.
```

Session state management:

- Session timeout: 180 seconds (3 minutes)
- Session ID is unique per user interaction
- Text parameter accumulates all inputs: `1*1234*1*2`
- Split by `*` to determine current step in flow

Rate limits:

- 100 requests per second per API key
- 10,000 sessions per day (sandbox)
- Unlimited (production with proper provisioning)

Error codes:

- 401: Authentication failed
- 400: Invalid parameters
- 429: Rate limit exceeded
- 500: Internal server error

Integration example (Django):

```python
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def ussd_gateway(request):
    session_id = request.POST.get('sessionId')
    phone = request.POST.get('phoneNumber')
    text = request.POST.get('text', '')

    steps = text.split('*') if text else []

    if len(steps) == 0:
        response = "CON Welcome to BimaGrid.\n1. Register\n2. Check Status"
    elif len(steps) == 1 and steps[0] == '1':
        response = "CON Enter Ward Code:"
    # ... more logic

    return HttpResponse(response, content_type='text/plain')
```

#### 2.2 Africa's Talking SMS API

Endpoint: `POST /messaging`

Base URL: https://api.africastalking.com/version1/

Request headers:

- Content-Type: application/x-www-form-urlencoded
- apiKey: YOUR_API_KEY
- Accept: application/json

Request parameters:

- username: string (required)
- to: string (required) - Comma-separated phone numbers
- message: string (required) - SMS content (max 160 chars per segment)
- from: string (optional) - Alphanumeric sender ID (shortcode)
- enqueue: boolean (optional) - Queue for bulk sending

Request example:

```http
POST /messaging HTTP/1.1
Content-Type: application/x-www-form-urlencoded
apiKey: atksk_XXXXXXXXXXXXXXXXXXXX

username=myUsername&to=254712345678,254723456789&message=BimaGrid: Drought detected. Payout of KES 5,000 initiated.&from=BimaGrid
```

Response format (JSON):

```json
{
  "SMSMessageData": {
    "Message": "Sent to 2/2 Total Cost: KES 1.60",
    "Recipients": [
      {
        "statusCode": "101",
        "number": "+254712345678",
        "status": "Success",
        "cost": "KES 0.80",
        "messageId": "ATXid_123456789"
      },
      {
        "statusCode": "101",
        "number": "+254723456789",
        "status": "Success",
        "cost": "KES 0.80",
        "messageId": "ATXid_987654321"
      }
    ]
  }
}
```

Delivery reports:

- Enable via callback URL in dashboard
- Webhook receives delivery status updates
- Status codes: 1 (Success), 2 (Failed), 3 (Rejected)

Rate limits:

- 100 SMS per second
- 1,000,000 SMS per day (production)

Pricing:

- Kenya: KES 0.80 per SMS
- Bulk discounts available

Integration example:

```python
```

## 3. Payment APIs

### 3.1 Safaricom M-Pesa Daraja API

Provider: Safaricom (Kenya)

Base URL:

- https://sandbox.safaricom.co.ke (sandbox)
- https://api.safaricom.co.ke (production)

Documentation: https://developer.safaricom.co.ke

Purpose:

- STK Push (Lipa Na M-Pesa Online)
- B2C (Business to Customer) payouts
- C2B (Customer to Business) premium collection
- Transaction status queries

Authentication:

- Method: OAuth 2.0 Bearer Token
- Endpoint: POST /oauth/v1/generate?grant_type=client_credentials
- Credentials: Consumer Key + Consumer Secret (Basic Auth)
- Token validity: 3599 seconds (1 hour)

Token generation:

```bash
```

Response:

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": "3599"
}
```

#### 3.1.1 STK Push (Lipa Na M-Pesa Online)

Endpoint: `POST /mpesa/stkpush/v1/processrequest`

Purpose: Trigger M-Pesa PIN entry on customer's phone

Request headers:

- Authorization: Bearer YOUR_ACCESS_TOKEN
- Content-Type: application/json

Request body:

```json
{
  "BusinessShortCode": "174379",
  "Password": "BASE64(ShortCode+Passkey+Timestamp)",
  "Timestamp": "20260701143000",
  "TransactionType": "CustomerPayBillOnline",
  "Amount": "250",
  "PartyA": "254712345678",
  "PartyB": "174379",
  "PhoneNumber": "254712345678",
  "CallBackURL": "https://bimagrid.io/api/payments/mpesa/callback/",
  "AccountReference": "POL-98765",
  "TransactionDesc": "BimaGrid Premium Payment"
}
```

Password generation:

```python
```

Response:

```json
{
  "MerchantRequestID": "12345-67890-12345",
  "CheckoutRequestID": "ws_CO_01072026143000123",
  "ResponseCode": "0",
  "ResponseDescription": "Success. Request accepted for processing",
  "CustomerMessage": "Success. Request accepted for processing"
}
```

Callback webhook:

`POST /api/payments/mpesa/callback/`

Request body:

```json
{
  "Body": {
    "stkCallback": {
      "MerchantRequestID": "12345-67890-12345",
      "CheckoutRequestID": "ws_CO_01072026143000123",
      "ResultCode": 0,
      "ResultDesc": "The service request is processed successfully.",
      "CallbackMetadata": {
        "Item": [
          {"Name": "Amount", "Value": 250.00},
          {"Name": "MpesaReceiptNumber", "Value": "QJG3K5X8Y9"},
          {"Name": "Balance"},
          {"Name": "TransactionDate", "Value": 20260701143015},
          {"Name": "PhoneNumber", "Value": 254712345678}
        ]
      }
    }
  }
}
```

Result codes:

- 0: Success
- 1032: Request cancelled by user
- 1037: DS timeout (user didn't enter PIN)
- 1: Balance insufficient
- 4: Invalid account

Rate limits:

- 100 requests per second
- 10,000 transactions per day (sandbox)

Integration example:

```python
```

#### 3.1.2 B2C (Business to Customer) Payouts

Endpoint: `POST /mpesa/b2c/v1/paymentrequest`

Purpose: Send payouts to farmers after claim approval

Request body:

```json
{
  "InitiatorName": "BimaGridAdmin",
  "SecurityCredential": "ENCRYPTED_CREDENTIAL",
  "CommandID": "BusinessPayment",
  "Amount": "5000",
  "PartyA": "600123",
  "PartyB": "254712345678",
  "Remarks": "Drought claim payout",
  "QueueTimeOutURL": "https://bimagrid.io/api/payments/mpesa/timeout/",
  "ResultURL": "https://bimagrid.io/api/payments/mpesa/result/",
  "Occasion": "Claim POL-98765"
}
```

Security credential generation:

```python
```

Response:

```json
{
  "ConversationID": "AG_20260701_0000123456",
  "OriginatorConversationID": "12345-67890-12345",
  "ResponseDescription": "Accept the service request successfully."
}
```

Result callback:

`POST /api/payments/mpesa/result/`

```json
{
  "Result": {
    "ResultType": 0,
    "ResultCode": 0,
    "ResultDesc": "The service request is processed successfully.",
    "OriginatorConversationID": "12345-67890-12345",
    "ConversationID": "AG_20260701_0000123456",
    "TransactionID": "QJG3K5X8Y9",
    "ResultParameters": {
      "ResultParameter": [
        {"Key": "TransactionAmount", "Value": 5000},
        {"Key": "TransactionReceipt", "Value": "QJG3K5X8Y9"},
        {"Key": "B2CRecipientIsRegisteredCustomer", "Value": "Y"},
        {"Key": "B2CChargesPaidAccountAvailableFunds", "Value": 100000},
        {"Key": "ReceiverPartyPublicName", "Value": "John Doe - 254712345678"},
        {"Key": "TransactionCompletedDateTime", "Value": "01.07.2026 14:35:20"},
        {"Key": "B2CUtilityAccountAvailableFunds", "Value": 50000}
      ]
    }
  }
}
```

Rate limits:

- 50 requests per second
- 5,000 transactions per day

Charges:

- KES 20 per transaction (up to KES 10,000)
- KES 50 per transaction (KES 10,001 - 30,000)
- KES 75 per transaction (above KES 30,000)

## 4. Government Integration APIs

### 4.1 IPRS (Integrated Population Registration System)

Provider: Government of Kenya (Ministry of Interior)

Base URL: https://iprs.go.ke/api/v1/

Documentation: Internal (requires MOU with government)

Purpose:

- Verify National ID numbers
- Validate identity details (name, DOB, gender)
- KYC/AML compliance
- Fraud prevention

Authentication:

- Method: Mutual TLS + API Key
- Certificate: X.509 client certificate
- Header: X-API-Key: YOUR_API_KEY
- IP Whitelisting: Required

Identity verification endpoint:

`POST /identity/verify`

Request body:

```json
{
  "id_number": "12345678",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-05-15"
}
```

Response:

```json
{
  "status": "verified",
  "confidence_score": 0.98,
  "details": {
    "id_number": "12345678",
    "full_name": "John Doe",
    "date_of_birth": "1990-05-15",
    "gender": "M",
    "registration_date": "2005-03-20",
    "status": "ACTIVE"
  }
}
```

Response statuses:

- verified: All details match
- partial_match: Some details match (requires manual review)
- not_found: ID number not in system
- mismatch: Details don't match

Rate limits:

- 10 requests per second
- 100,000 verifications per day

Compliance requirements:

- Data Processing Agreement (DPA) required
- Annual security audit
- Data retention: Max 7 years
- Purpose limitation: Only for identity verification

Integration example:

```python
```

### 4.2 ArdhiSasa (National Land Registry)

Provider: Ministry of Lands (Kenya)

Base URL: https://ardhisasa.lands.go.ke/api/v1/

Documentation: https://ardhisasa.lands.go.ke/docs

Purpose:

- Verify land title deeds
- Check ownership records
- Validate parcel numbers
- Detect encumbrances

Authentication:

- Method: OAuth 2.0
- Client credentials flow
- Token validity: 1 hour

Title verification endpoint:

`POST /title/verify`

Request body:

```json
{
  "title_number": "LR/12345",
  "owner_id_number": "12345678",
  "parcel_number": "Nakuru/Block1/234"
}
```

Response:

```json
{
  "status": "verified",
  "title_details": {
    "title_number": "LR/12345",
    "parcel_number": "Nakuru/Block1/234",
    "owner_name": "John Doe",
    "owner_id": "12345678",
    "land_area_hectares": 2.5,
    "land_use": "Agricultural",
    "registration_date": "2010-05-15",
    "encumbrances": [],
    "status": "ACTIVE"
  }
}
```

Encumbrance types:

- mortgage: Property used as collateral
- caveat: Legal claim against property
- lien: Right to keep possession until debt paid
- easement: Right to use another's land

Rate limits:

- 5 requests per second
- 10,000 queries per day

Integration example:

```python
```

## 5. Weather & Climate Data APIs

### 5.1 CHIRPS (Climate Hazards Group Infrared Precipitation)

Provider: UC Santa Barbara

Base URL: https://data.chc.ucsb.edu/products/CHIRPS-2.0/

Format: GeoTIFF, NetCDF

Resolution: 0.05° × 0.05° (~5km × ~5km)

Temporal: Daily, Monthly

Latency: 1-3 days (final), Real-time (CHIRPS-RT)

Purpose:

- Historical rainfall analysis (20-year baseline)
- Drought monitoring
- Parametric trigger calculation

Data access methods:

#### Method 1: Direct FTP/HTTP Download

URL: https://data.chc.ucsb.edu/products/CHIRPS-2.0/africa_daily/tifs/p05/

File naming:

- chirps-v2.0.YYYY.MM.DD.p05.tif

Example:

- chirps-v2.0.2026.06.15.p05.tif

#### Method 2: Google Earth Engine

Collection: UCSB-CHG/CHIRPS/DAILY

Variables:

- precipitation: Daily precipitation (mm)

Example (Python):

```python
```

#### Method 3: CHIRPS API (Limited)

Base URL: https://chcdata.org/api/

Endpoint: `GET /chirps/daily`

Parameters:

- lat: float (latitude)
- lon: float (longitude)
- start_date: YYYY-MM-DD
- end_date: YYYY-MM-DD

Response:

```json
{
  "location": {"lat": -1.2921, "lon": 36.8219},
  "data": [
    {"date": "2026-06-01", "precipitation": 12.5},
    {"date": "2026-06-02", "precipitation": 8.3}
  ]
}
```

Rate limits:

- 100 requests per hour
- No authentication required (but recommended)

Usage in BimaGrid:

```python
```

### 5.2 NASA POWER (Prediction of Worldwide Energy Resources)

Provider: NASA

Base URL: https://power.larc.nasa.gov/api/

Resolution: 0.5° × 0.625°

Temporal: Hourly, Daily, Monthly, Annual, Climatology

Purpose:

- Temperature data (frost, heat stress)
- Humidity (pest/disease risk)
- Solar radiation (crop growth)
- Wind speed (windstorm risk)

Authentication:

- Method: API Key (optional but recommended)
- Header: api_key=YOUR_API_KEY
- Rate limit increase with registration

Endpoints:

Community Access (Point Data)

`GET /point/daily/historical`

Parameters:

- parameters: Comma-separated list (T2M, RH2M, ALLSKY_SFC_SW_DWN)
- community: RE (Renewable Energy), AG (Agriculture), SB (Sustainable Buildings)
- longitude: float
- latitude: float
- start: YYYYMMDD
- end: YYYYMMDD
- format: JSON, CSV

Example request:

```http
GET https://power.larc.nasa.gov/api/point/daily/historical?parameters=T2M,RH2M&community=AG&longitude=36.82&latitude=-1.29&start=20260601&end=20260630&format=JSON
```

Response:

```json
{
  "parameters": {
    "T2M": {
      "20260601": 22.5,
      "20260602": 23.1
    },
    "RH2M": {
      "20260601": 65.2,
      "20260602": 68.4
    }
  },
  "header": {
    "title": "NASA POWER Historical Daily Data",
    "fill_value": -999,
    "start": "20260601",
    "end": "20260630"
  }
}
```

Available parameters (Agriculture Community):

- T2M: Temperature at 2m (°C)
- T2M_MAX: Maximum temperature (°C)
- T2M_MIN: Minimum temperature (°C)
- RH2M: Relative humidity at 2m (%)
- PRECTOT: Precipitation (mm/day)
- ALLSKY_SFC_SW_DWN: All-sky surface shortwave downward (kWh/m²/day)
- WS2M: Wind speed at 2m (m/s)
- GWETTOP: Wetness status of top soil layer (0-1)

Rate limits:

- 500 requests per hour (unregistered)
- 5,000 requests per hour (registered)

Integration example:

```python
```

### 5.3 Open-Meteo API

Provider: Open-Meteo (Open-source)

Base URL: https://api.open-meteo.com/

Resolution: ~11km (global), ~2km (Europe)

Temporal: Hourly, Daily

Latency: Real-time to 1 hour

Purpose:

- Real-time weather data
- Weather forecasts
- Historical weather data
- Multi-peril monitoring

Authentication:

- Method: None required (free tier)
- Rate limit: 10,000 requests per day
- Commercial plans available for higher limits

Endpoints:

Forecast API

`GET /v1/forecast`

Parameters:

- latitude: float (required)
- longitude: float (required)
- hourly: Comma-separated list of hourly variables
- daily: Comma-separated list of daily variables
- timezone: string (e.g., "Africa/Nairobi")
- start_date: YYYY-MM-DD
- end_date: YYYY-MM-DD

Example request:

```http
GET https://api.open-meteo.com/v1/forecast?latitude=-1.29&longitude=36.82&daily=precipitation_sum,temperature_2m_max,temperature_2m_min&timezone=Africa/Nairobi&start_date=2026-06-01&end_date=2026-06-30
```

Response:

```json
{
  "latitude": -1.29,
  "longitude": 36.82,
  "generationtime_ms": 0.123,
  "utc_offset_seconds": 10800,
  "timezone": "Africa/Nairobi",
  "timezone_abbreviation": "EAT",
  "elevation": 1795.0,
  "daily": {
    "time": ["2026-06-01", "2026-06-02"],
    "precipitation_sum": [12.5, 8.3],
    "temperature_2m_max": [28.5, 29.1],
    "temperature_2m_min": [15.2, 16.0]
  }
}
```

Available variables:

Hourly:

- temperature_2m: Temperature at 2m (°C)
- relative_humidity_2m: Relative humidity (%)
- precipitation: Precipitation (mm)
- rain: Rain (mm)
- snowfall: Snowfall (cm)
- weathercode: Weather condition code
- cloudcover: Cloud cover (%)
- windspeed_10m: Wind speed at 10m (km/h)
- winddirection_10m: Wind direction (°)

Daily:

- temperature_2m_max: Maximum temperature (°C)
- temperature_2m_min: Minimum temperature (°C)
- precipitation_sum: Total precipitation (mm)
- rain_sum: Total rain (mm)
- snowfall_sum: Total snowfall (cm)
- precipitation_hours: Hours with precipitation
- weathercode: Dominant weather condition
- windspeed_10m_max: Maximum wind speed (km/h)
- windgusts_10m_max: Maximum wind gusts (km/h)

Weather codes:

- 0: Clear sky
- 1, 2, 3: Mainly clear, partly cloudy, overcast
- 45, 48: Fog
- 51, 53, 55: Drizzle
- 61, 63, 65: Rain
- 71, 73, 75: Snow
- 80, 81, 82: Rain showers
- 95: Thunderstorm
- 96, 99: Thunderstorm with hail

Rate limits:

- 10,000 requests per day (free)
- No authentication required

Integration example:

```python
```

## 6. Satellite & Earth Observation APIs

### 6.1 openEO API

Provider: openEO Consortium (multiple backends)

Base URL: Varies by backend

- Google Earth Engine: https://earthengine.openeo.org
- Sentinel Hub: https://openeo.sentinel-hub.com
- VITO: https://openeo.vito.be

Purpose:

- Serverless satellite data processing
- NDVI, NDWI, and other index calculations
- Crop health monitoring
- Mitigation verification (irrigation detection)

Authentication:

- Method: OpenID Connect (OIDC) or Basic Auth
- OIDC: Browser-based authentication
- Basic: Username/password (for GEE backend)

Core concepts:

- Collections: Satellite data products (Sentinel-2, Sentinel-1, etc.)
- Processes: Operations on data (filter, reduce, calculate)
- Process Graph: Chain of processes forming an algorithm
- Datacube: Multi-dimensional data structure (space, time, bands)
- Batch Job: Asynchronous processing task

API endpoints:

Discovery

- `GET /`
- `GET /collections`
- `GET /processes`
- `GET /file_formats`

Authentication

- `POST /credentials/oidc`
- `POST /credentials/basic`

Data processing

- `POST /result` (synchronous)
- `POST /jobs` (batch job)
- `GET /jobs/{job_id}`
- `POST /jobs/{job_id}/results`

Process graph example (NDVI calculation):

```json
```

Python client example:

```python
```

Available collections:

- Sentinel-2 (Optical):
  - Resolution: 10m (visible), 20m (red edge), 60m (atmospheric)
  - Revisit: 5 days
  - Bands: 13 spectral bands
  - Use: NDVI, crop health, land cover
- Sentinel-1 (Radar):
  - Resolution: 10m
  - Type: SAR (Synthetic Aperture Radar)
  - Polarizations: VV, VH
  - Use: Flood mapping, soil moisture (all-weather)
- Landsat:
  - Resolution: 30m
  - Revisit: 16 days
  - Use: Historical analysis, long-term trends
- MODIS:
  - Resolution: 250m - 1km
  - Revisit: Daily
  - Use: Large-scale monitoring

Rate limits:

- Varies by backend
- Google Earth Engine: 100 concurrent requests
- Sentinel Hub: Depends on subscription tier

Pricing:

- Google Earth Engine: Free for research, commercial pricing available
- Sentinel Hub: Pay-per-use (processing units)
- VITO: Subscription-based

Integration in BimaGrid:

```python
```

### 6.2 Sentinel Hub API

Provider: Sinergise (official Sentinel data distributor)

Base URL: https://services.sentinel-hub.com/

Documentation: https://docs.sentinel-hub.com/

Purpose:

- Direct access to Sentinel satellite data
- Advanced processing capabilities
- Custom evalscripts (JavaScript)

Authentication:

- Method: OAuth 2.0
- Client credentials flow
- Token validity: 1 hour

Token endpoint:

`POST https://services.sentinel-hub.com/oauth/token`

Request:

```text
grant_type=client_credentials&client_id=YOUR_ID&client_secret=YOUR_SECRET
```

Response:

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

Processing API:

`POST /api/v1/process`

Request body:

```json
{
  "input": {
    "bounds": {
      "bbox": [36.8, -1.3, 36.9, -1.2]
    },
    "data": [
      {
        "type": "sentinel-2-l2a",
        "dataFilter": {
          "timeRange": {
            "from": "2026-06-01T00:00:00Z",
            "to": "2026-06-30T23:59:59Z"
          },
          "mosaickingOrder": "leastCC"
        }
      }
    ]
  },
  "output": {
    "width": 512,
    "height": 512,
    "responses": [
      {
        "identifier": "default",
        "format": {"type": "image/png"}
      }
    ]
  },
  "evalscript": "//VERSION=3\nfunction setup() {\n return {\n input: [\"B04\", \"B08\"],\n output: { bands: 1 }\n };\n}\n\nfunction evaluatePixel(sample) {\n let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);\n return [ndvi];\n}"
}
```

Evalscript example (NDVI):

```javascript
```

Rate limits:

- Depends on subscription tier
- Free tier: 100,000 processing units per month
- Processing units calculated based on area and complexity

Pricing:

- Pay-per-use model
- Processing units consumed based on:
  - Area processed
  - Number of bands
  - Processing complexity

## 7. Blockchain Protocols

### 7.1 Custom Rust Blockchain

Architecture:

- Consensus: Proof of Authority (PoA)
- Execution: REVM (Rust EVM)
- Storage: Redb / RocksDB
- Networking: libp2p
- JSON-RPC: Ethereum-compatible

JSON-RPC endpoints:

Base URL: http://localhost:8545

#### eth_sendRawTransaction

`POST /`

Request:

```json
{
  "jsonrpc": "2.0",
  "method": "eth_sendRawTransaction",
  "params": ["0xf86c0a8502540be40082520894..."],
  "id": 1
}
```

Response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x88df016429689c079f3b2f6ad39fa052532c56795b733da78a91ebe6a713944b"
}
```

#### eth_call

`POST /`

Request:

```json
{
  "jsonrpc": "2.0",
  "method": "eth_call",
  "params": [
    {
      "to": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
      "data": "0x..."
    },
    "latest"
  ],
  "id": 1
}
```

Response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x000000000000000000000000000000000000000000000000000000000000002a"
}
```

#### eth_getTransactionReceipt

`POST /`

Request:

```json
{
  "jsonrpc": "2.0",
  "method": "eth_getTransactionReceipt",
  "params": ["0x88df016429689c079f3b2f6ad39fa052532c56795b733da78a91ebe6a713944b"],
  "id": 1
}
```

Response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "transactionHash": "0x88df016429689c079f3b2f6ad39fa052532c56795b733da78a91ebe6a713944b",
    "blockNumber": "0x1b4",
    "blockHash": "0x26c5b4...",
    "from": "0x407d73d8a49eeb85d32cf465507dd71d507100c1",
    "to": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
    "gasUsed": "0x7a120",
    "cumulativeGasUsed": "0x7a120",
    "contractAddress": null,
    "logs": [...],
    "status": "0x1"
  }
}
```

#### eth_getLogs

`POST /`

Request:

```json
{
  "jsonrpc": "2.0",
  "method": "eth_getLogs",
  "params": [
    {
      "fromBlock": "0x1",
      "toBlock": "latest",
      "address": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
      "topics": ["0x..."]
    }
  ],
  "id": 1
}
```

Response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    {
      "address": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
      "topics": ["0x...", "0x..."],
      "data": "0x...",
      "blockNumber": "0x1b4",
      "transactionHash": "0x88df...",
      "blockHash": "0x26c5...",
      "logIndex": "0x0"
    }
  ]
}
```

#### Block Structure

```json
{
  "number": "0x1b4",
  "hash": "0x26c5b4...",
  "parentHash": "0x1a3b2c...",
  "nonce": "0x0000000000000042",
  "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
  "logsBloom": "0x...",
  "transactionsRoot": "0x...",
  "stateRoot": "0x...",
  "receiptsRoot": "0x...",
  "miner": "0x0000000000000000000000000000000000000000",
  "difficulty": "0x0",
  "totalDifficulty": "0x0",
  "extraData": "0x",
  "size": "0x27f",
  "gasLimit": "0x1c9c380",
  "gasUsed": "0x7a120",
  "timestamp": "0x5f2e5c80",
  "transactions": ["0x88df..."],
  "uncles": []
}
```

#### Transaction Structure

```json
{
  "hash": "0x88df016429689c079f3b2f6ad39fa052532c56795b733da78a91ebe6a713944b",
  "nonce": "0xa",
  "blockHash": "0x26c5b4...",
  "blockNumber": "0x1b4",
  "transactionIndex": "0x0",
  "from": "0x407d73d8a49eeb85d32cf465507dd71d507100c1",
  "to": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
  "value": "0x0",
  "gasPrice": "0x2540be400",
  "gas": "0x5208",
  "input": "0x..."
}
```

Consensus mechanism:

- Proof of Authority (PoA)
- 3 validator nodes
- Round-robin block proposal
- Instant finality
- Block time: 5 seconds

Validator rotation:

- Validator 1 proposes block N
- Validators 2 and 3 sign block N
- Validator 2 proposes block N+1
- Validators 1 and 3 sign block N+1
- Continue rotation

Finality:

- Blocks are final once signed by 2/3 validators
- No reorgs possible after finality
- Suitable for financial applications

Network topology:

- 3 validator nodes (full nodes)
- Peer-to-peer networking via libp2p
- Gossip protocol for transaction propagation
- Block propagation via direct messaging

## 8. Authentication Protocols

### 8.1 OAuth 2.0

Flow: Authorization Code Flow (for user-facing applications)

Endpoints:

- Authorization: /oauth/authorize
- Token: /oauth/token
- Refresh: /oauth/token (with refresh_token grant)

Authorization request:

```http
GET /oauth/authorize?
response_type=code&
client_id=YOUR_CLIENT_ID&
redirect_uri=https://bimagrid.io/callback&
scope=read write&
state=RANDOM_STATE_STRING
```

Response (Redirect):

```http
HTTP/1.1 302 Found
Location: https://bimagrid.io/callback?code=AUTHORIZATION_CODE&state=RANDOM_STATE_STRING
```

Token exchange:

```http
POST /oauth/token
```

Request:

```text
grant_type=authorization_code&
code=AUTHORIZATION_CODE&
redirect_uri=https://bimagrid.io/callback&
client_id=YOUR_CLIENT_ID&
client_secret=YOUR_CLIENT_SECRET
```

Response:

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
  "scope": "read write"
}
```

Token refresh:

```http
POST /oauth/token
```

Request:

```text
grant_type=refresh_token&
refresh_token=tGzv3JOkF0XG5Qx2TlKWIA&
client_id=YOUR_CLIENT_ID&
client_secret=YOUR_CLIENT_SECRET
```

Response:

```json
{
  "access_token": "NEW_ACCESS_TOKEN",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "NEW_REFRESH_TOKEN"
}
```

Security best practices:

- Use HTTPS for all endpoints
- Validate `redirect_uri` against whitelist
- Use `state` parameter to prevent CSRF
- Store tokens securely (encrypted at rest)
- Implement token rotation
- Use short-lived access tokens (1 hour)
- Use long-lived refresh tokens (30 days)

### 8.2 OpenID Connect (OIDC)

Built on: OAuth 2.0

Adds: Identity layer (ID Token)

ID token:

JWT containing user identity information.

JWT structure:

`Header.Payload.Signature`

Header:

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "key-id-123"
}
```

Payload:

```json
{
  "iss": "https://auth.bimagrid.io",
  "sub": "user-123",
  "aud": "YOUR_CLIENT_ID",
  "exp": 1625145600,
  "iat": 1625142000,
  "nonce": "RANDOM_NONCE",
  "name": "John Doe",
  "email": "john@example.com",
  "phone_number": "+254712345678"
}
```

Signature:

`RS256(base64(header) + "." + base64(payload), private_key)`

Discovery endpoint:

`GET /.well-known/openid-configuration`

Response:

```json
{
  "issuer": "https://auth.bimagrid.io",
  "authorization_endpoint": "https://auth.bimagrid.io/authorize",
  "token_endpoint": "https://auth.bimagrid.io/token",
  "userinfo_endpoint": "https://auth.bimagrid.io/userinfo",
  "jwks_uri": "https://auth.bimagrid.io/.well-known/jwks.json",
  "scopes_supported": ["openid", "profile", "email", "phone"],
  "response_types_supported": ["code", "token", "id_token"],
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "subject_types_supported": ["public"],
  "id_token_signing_alg_values_supported": ["RS256"]
}
```

UserInfo endpoint:

`GET /userinfo`

Headers:

- Authorization: Bearer ACCESS_TOKEN

Response:

```json
{
  "sub": "user-123",
  "name": "John Doe",
  "email": "john@example.com",
  "email_verified": true,
  "phone_number": "+254712345678",
  "phone_number_verified": false
}
```

### 8.3 API Key Authentication

Method: API key in header or query parameter

Header method (preferred):

```http
GET /api/v1/farmers
X-API-Key: YOUR_API_KEY
```

Query parameter method (not recommended):

```http
GET /api/v1/farmers?api_key=YOUR_API_KEY
```

API key generation:

- Generate using cryptographically secure random number generator
- Minimum 32 bytes (256 bits)
- Prefix with identifier (e.g., `bg_` for BimaGrid)
- Example: `bg_1a2b3c4d5e6f7g8h9i0j...`

API key storage:

- Hash with bcrypt or Argon2
- Store hash, not plaintext
- Associate with user/organization
- Track usage and rate limits

API key validation:

```python
```

Rate limiting by API key:

- Track requests per API key
- Enforce limits (e.g., 1000 requests/hour)
- Return 429 Too Many Requests when exceeded

### 8.4 JWT (JSON Web Token)

Structure: Header.Payload.Signature

Header:

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

Payload (Claims):

```json
{
  "sub": "user-123",
  "name": "John Doe",
  "iat": 1625142000,
  "exp": 1625145600,
  "roles": ["farmer", "verified"]
}
```

Signature:

`HMACSHA256(base64(header) + "." + base64(payload), secret_key)`

JWT generation (Python):

```python
```

JWT validation:

```python
```

Security considerations:

- Use HTTPS for all JWT transmission
- Set appropriate expiration (short-lived)
- Validate signature on every request
- Don't store sensitive data in payload
- Use asymmetric keys (RS256) for production

## 9. Data Exchange Protocols

### 9.1 REST (Representational State Transfer)

Principles:

- Stateless: Each request contains all necessary information
- Client-Server: Separation of concerns
- Cacheable: Responses can be cached
- Layered System: Intermediary servers allowed
- Uniform Interface: Consistent API design

HTTP methods:

- GET: Retrieve resource
- POST: Create resource
- PUT: Update resource (full replacement)
- PATCH: Update resource (partial)
- DELETE: Remove resource

Status codes:

- 200 OK: Success
- 201 Created: Resource created
- 204 No Content: Success, no response body
- 400 Bad Request: Invalid request
- 401 Unauthorized: Authentication required
- 403 Forbidden: Authenticated but not authorized
- 404 Not Found: Resource doesn't exist
- 429 Too Many Requests: Rate limit exceeded
- 500 Internal Server Error: Server error

Request example:

```http
GET /api/v1/farmers/123 HTTP/1.1
Host: api.bimagrid.io
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
```

Response example:

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "id": 123,
  "name": "John Doe",
  "phone": "+254712345678",
  "ward_code": "1234",
  "created_at": "2026-01-15T10:30:00Z"
}
```

Pagination:

```http
GET /api/v1/farmers?page=2&per_page=20
```

Response:

```json
{
  "data": [],
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

Filtering:

```http
GET /api/v1/farmers?ward_code=1234&crop=maize&status=active
```

Sorting:

```http
GET /api/v1/farmers?sort=-created_at,name
```

Field selection:

```http
GET /api/v1/farmers?fields=id,name,phone
```

### 9.2 GraphQL

Purpose: Flexible data querying, avoid over/under-fetching

Endpoint: `POST /graphql`

Query example:

```json
{
  "query": "query { farmer(id: 123) { id name phone policies { id crop acreage } } }"
}
```

Response:

```json
{
  "data": {
    "farmer": {
      "id": 123,
      "name": "John Doe",
      "phone": "+254712345678",
      "policies": [
        {
          "id": 456,
          "crop": "maize",
          "acreage": 2.5
        }
      ]
    }
  }
}
```

Mutation example:

```json
{
  "query": "mutation { createFarmer(input: {name: \"John Doe\", phone: \"+254712345678\"}) { id name } }"
}
```

Response:

```json
{
  "data": {
    "createFarmer": {
      "id": 123,
      "name": "John Doe"
    }
  }
}
```

Schema definition:

```graphql
type Farmer {
  id: ID!
  name: String!
  phone: String!
  wardCode: String!
  policies: [Policy!]!
  createdAt: DateTime!
}

type Policy {
  id: ID!
  crop: String!
  acreage: Float!
  premium: Float!
  status: PolicyStatus!
}

enum PolicyStatus {
  ACTIVE
  EXPIRED
  CANCELLED
}

type Query {
  farmer(id: ID!): Farmer
  farmers(wardCode: String, crop: String): [Farmer!]!
}

type Mutation {
  createFarmer(input: CreateFarmerInput!): Farmer!
  updateFarmer(id: ID!, input: UpdateFarmerInput!): Farmer!
}

input CreateFarmerInput {
  name: String!
  phone: String!
  wardCode: String!
}
```

Advantages:

- Client specifies exactly what data it needs
- Single endpoint for all queries
- Strongly typed schema
- Introspection (self-documenting)
- No over-fetching or under-fetching

Disadvantages:

- Complex to implement
- Caching more difficult
- Query complexity can be high
- Learning curve for developers

### 9.3 WebSockets

Purpose: Real-time bidirectional communication

Protocol: `ws://` (unencrypted) or `wss://` (encrypted)

Connection:

- WebSocket handshake via HTTP Upgrade

Request:

```http
GET /ws HTTP/1.1
Host: api.bimagrid.io
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

Response:

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

Messaging:

- Once connected, messages can be sent bidirectionally

Client message:

```json
{
  "type": "subscribe",
  "channel": "payouts",
  "farmer_id": 123
}
```

Server message:

```json
{
  "type": "payout",
  "data": {
    "policy_id": 456,
    "amount": 5000,
    "status": "completed",
    "timestamp": "2026-07-01T14:30:00Z"
  }
}
```

Use cases in BimaGrid:

- Real-time payout notifications
- Live oracle data updates
- Admin dashboard real-time stats
- USSD session state synchronization

Implementation (Python):

```python
```

## 10. Webhook Protocols

### 10.1 Webhook Structure

Purpose: Receive real-time notifications from external services

Delivery method: HTTP POST with JSON payload

Headers:

- Content-Type: application/json
- X-Webhook-Signature: HMAC signature (for verification)
- X-Webhook-ID: Unique webhook delivery ID
- X-Webhook-Timestamp: Unix timestamp

Request body:

```json
{
  "event": "payout.completed",
  "timestamp": "2026-07-01T14:30:00Z",
  "data": {
    "policy_id": 456,
    "farmer_id": 123,
    "amount": 5000,
    "transaction_id": "QJG3K5X8Y9"
  }
}
```

Response:

- 200 OK: Webhook received successfully
- 4xx: Client error (don't retry)
- 5xx: Server error (retry with exponential backoff)

### 10.2 Webhook Security

Signature verification:

- Prevent spoofing by verifying webhook signature

Signature generation (Sender):

```python
```

Signature verification (Receiver):

```python
```

Timestamp verification:

- Prevent replay attacks by checking timestamp

```python
```

### 10.3 Webhook Retry Policy

Retry strategy:

- Exponential backoff
- Maximum 5 retries
- Retry on 5xx errors only

Retry schedule:

- First retry: 1 minute
- Second retry: 5 minutes
- Third retry: 30 minutes
- Fourth retry: 2 hours
- Fifth retry: 24 hours

Dead letter queue:

- After 5 failed attempts, move to dead letter queue for manual inspection

### 10.4 M-Pesa Webhooks

#### STK Push Callback

`POST /api/payments/mpesa/callback/`

Payload:

```json
{
  "Body": {
    "stkCallback": {
      "MerchantRequestID": "12345-67890-12345",
      "CheckoutRequestID": "ws_CO_01072026143000123",
      "ResultCode": 0,
      "ResultDesc": "The service request is processed successfully.",
      "CallbackMetadata": {
        "Item": [
          {"Name": "Amount", "Value": 250.00},
          {"Name": "MpesaReceiptNumber", "Value": "QJG3K5X8Y9"},
          {"Name": "TransactionDate", "Value": 20260701143015},
          {"Name": "PhoneNumber", "Value": 254712345678}
        ]
      }
    }
  }
}
```

#### B2C Result Callback

`POST /api/payments/mpesa/result/`

Payload:

```json
{
  "Result": {
    "ResultType": 0,
    "ResultCode": 0,
    "ResultDesc": "The service request is processed successfully.",
    "OriginatorConversationID": "12345-67890-12345",
    "ConversationID": "AG_20260701_0000123456",
    "TransactionID": "QJG3K5X8Y9",
    "ResultParameters": {
      "ResultParameter": [
        {"Key": "TransactionAmount", "Value": 5000},
        {"Key": "TransactionReceipt", "Value": "QJG3K5X8Y9"},
        {"Key": "ReceiverPartyPublicName", "Value": "John Doe - 254712345678"},
        {"Key": "TransactionCompletedDateTime", "Value": "01.07.2026 14:35:20"}
      ]
    }
  }
}
```

#### B2C Timeout Callback

`POST /api/payments/mpesa/timeout/`

Payload:

```json
{
  "Result": {
    "ResultType": 0,
    "ResultCode": 1032,
    "ResultDesc": "The service request was timed out.",
    "OriginatorConversationID": "12345-67890-12345",
    "ConversationID": "AG_20260701_0000123456"
  }
}
```

## 11. API Security Standards

### 11.1 Transport Security

Requirements:

- TLS 1.2 minimum (TLS 1.3 recommended)
- Valid SSL certificates (Let's Encrypt or commercial)
- HSTS (HTTP Strict Transport Security)
- Certificate pinning (mobile apps)

HSTS header:

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

Cipher suites (recommended):

- TLS_AES_256_GCM_SHA384
- TLS_CHACHA20_POLY1305_SHA256
- TLS_AES_128_GCM_SHA256

### 11.2 Input Validation

Principles:

- Validate all input (never trust client)
- Use allowlists over denylists
- Validate type, length, format, range
- Sanitize output (prevent XSS)

Example (Python):

```python
```

### 11.3 SQL Injection Prevention

Method: Use parameterized queries (ORM)

Vulnerable code:

```python
```

Secure code:

```python
```

### 11.4 XSS (Cross-Site Scripting) Prevention

Method: Sanitize output, use Content Security Policy

Sanitization (Python):

```python
```

Content Security Policy header:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted.cdn.com
```

### 11.5 CSRF (Cross-Site Request Forgery) Prevention

Method: CSRF tokens for state-changing operations

Token generation:

```python
```

Token validation:

```python
```

### 11.6 Rate Limiting

Method: Prevent abuse and DDoS

Implementation:

```python
```

### 11.7 Secret Management

Principles:

- Never hardcode secrets
- Use environment variables
- Rotate secrets regularly
- Use secret management services

Environment variables:

```bash
```

Secret management services:

- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- GCP Secret Manager

## 12. Rate Limiting Policies

### 12.1 Rate Limiting Strategy

Algorithm: Sliding window counter

Implementation:

```python
```

### 12.2 Rate Limit Tiers

Free tier:

- 100 requests per hour
- 1,000 requests per day
- Basic API access

Pro tier:

- 1,000 requests per hour
- 10,000 requests per day
- Priority support

Enterprise tier:

- 10,000 requests per hour
- 100,000 requests per day
- Dedicated support
- Custom limits

### 12.3 Rate Limit Headers

Response headers:

- X-RateLimit-Limit: 100
- X-RateLimit-Remaining: 95
- X-RateLimit-Reset: 1625145600

Explanation:

- X-RateLimit-Limit: Maximum requests allowed
- X-RateLimit-Remaining: Requests remaining in current window
- X-RateLimit-Reset: Unix timestamp when limit resets

### 12.4 Rate Limit Exceeded Response

Status code: 429 Too Many Requests

Response body:

```json
{
  "error": "Rate limit exceeded",
  "message": "You have exceeded the rate limit of 100 requests per hour",
  "retry_after": 3600
}
```

Headers:

- Retry-After: 3600

## 13. Error Handling Standards

### 13.1 Error Response Format

Standard format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "phone",
        "message": "Invalid Kenyan phone number format"
      }
    ],
    "request_id": "req_123456789",
    "timestamp": "2026-07-01T14:30:00Z"
  }
}
```

Fields:

- code: Machine-readable error code
- message: Human-readable error message
- details: Array of field-specific errors (for validation)
- request_id: Unique request identifier (for debugging)
- timestamp: When error occurred

### 13.2 Error Codes

Authentication errors:

- AUTHENTICATION_REQUIRED: No authentication provided
- INVALID_CREDENTIALS: Wrong username/password
- TOKEN_EXPIRED: Access token expired
- INVALID_TOKEN: Malformed or invalid token
- INSUFFICIENT_PERMISSIONS: Not authorized for this action

Validation errors:

- VALIDATION_ERROR: Input validation failed
- INVALID_FORMAT: Invalid data format
- REQUIRED_FIELD: Missing required field
- INVALID_VALUE: Field value out of range
- DUPLICATE_ENTRY: Unique constraint violation

Resource errors:

- NOT_FOUND: Resource doesn't exist
- ALREADY_EXISTS: Resource already exists
- CONFLICT: Resource state conflict
- GONE: Resource permanently removed

Rate limit errors:

- RATE_LIMIT_EXCEEDED: Too many requests
- QUOTA_EXCEEDED: Usage quota exceeded

Server errors:

- INTERNAL_ERROR: Unexpected server error
- SERVICE_UNAVAILABLE: Service temporarily unavailable
- UPSTREAM_ERROR: Error from upstream service
- TIMEOUT: Request timeout

External API errors:

- EXTERNAL_API_ERROR: Error from external API
- MPESA_ERROR: M-Pesa API error
- USSD_ERROR: USSD gateway error
- WEATHER_API_ERROR: Weather data API error

### 13.3 Error Handling Middleware

Django example:

```python
```

### 13.4 Error Logging

Structured logging:

```python
```

Log levels:

- DEBUG: Detailed information for debugging
- INFO: General operational information
- WARNING: Something unexpected but not critical
- ERROR: Error occurred but system can continue
- CRITICAL: System cannot continue

## 14. API Versioning Strategy

### 14.1 Versioning Approach

Method: URL path versioning

Format: `/api/v{version}/resource`

Examples:

- `/api/v1/farmers`
- `/api/v2/farmers`

Rationale:

- Clear and explicit
- Easy to route
- Simple to understand
- Allows multiple versions to coexist

### 14.2 Version Lifecycle

Deprecation policy:

- Major versions supported for 2 years after successor release
- 6-month deprecation notice before end-of-life
- Migration guides provided for each major version
- Automated tools for migration where possible

Version timeline:

- v1.0.0: Initial release (2026-01-01)
- v1.1.0: Minor updates (2026-04-01)
- v2.0.0: Major release (2027-01-01)
- v1.x.x: Deprecated (2027-07-01)
- v1.x.x: End-of-life (2029-01-01)

### 14.3 Backward Compatibility

Rules:

- Never remove fields from responses
- Never change field types
- Never make optional fields required
- Never change URL structure
- Add new fields instead of modifying existing ones
- Use new endpoints for breaking changes

Example (Adding a field):

```json
```

Example (Breaking change):

```json
```

### 14.4 Version Negotiation

Header method (alternative):

```http
Accept: application/vnd.bimagrid.v1+json
```

Implementation:

```python
```

## 15. Monitoring & Observability

### 15.1 API Metrics

Key metrics:

- Request rate (requests per second)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Active connections
- Request size
- Response size

Implementation (Django):

```python
```

### 15.2 Logging Standards

Structured log format:

```json
```

Log levels:

- DEBUG: Development and debugging information
- INFO: Normal operational events
- WARNING: Unexpected events, potential issues
- ERROR: Errors that need attention
- CRITICAL: System-level failures

Sensitive data:

- Never log passwords, tokens, or secrets
- Mask PII (phone numbers, emails) in logs
- Use correlation IDs for request tracing

### 15.3 Distributed Tracing

OpenTelemetry setup:

```python
```

### 15.4 Health Checks

Endpoint: `GET /health`

Response:

```json
{
  "status": "healthy",
  "version": "1.2.0",
  "timestamp": "2026-07-01T14:30:00Z",
  "checks": {
    "database": "healthy",
    "redis": "healthy",
    "external_apis": {
      "mpesa": "healthy",
      "africastalking": "healthy",
      "weather_api": "degraded"
    }
  }
}
```

Implementation:

```python
```

## 16. API Testing Strategy

### 16.1 Testing Pyramid

Unit tests (70%):

- Test individual functions and methods
- Mock external dependencies
- Fast execution
- High coverage

Integration tests (20%):

- Test API endpoints
- Test database interactions
- Test external API integrations (with mocks)
- Medium execution time

End-to-end tests (10%):

- Test complete user flows
- Test real external APIs (in staging)
- Test UI interactions
- Slow execution

### 16.2 Unit Testing

Framework: pytest

Example:

```python
```

### 16.3 Integration Testing

Framework: pytest + Django test client

Example:

```python
```

### 16.4 External API Testing

Mocking strategy:

```python
```

Contract testing:

```python
```

### 16.5 Load Testing

Tool: Locust

Example:

```python
```

Run:

```bash
```

## 17. Compliance & Regulatory APIs

### 17.1 Insurance Regulatory Authority (IRA) Kenya

Requirements:

- Quarterly reporting of policies issued
- Claims settlement within 30 days
- Premium rate filing and approval
- Capital adequacy requirements
- Data protection compliance

Reporting API:

`POST https://api.ira.go.ke/v1/reports/quarterly`

Request body:

```json
{
  "quarter": "Q2-2026",
  "policies_issued": 15000,
  "premiums_collected_kes": 3750000,
  "claims_paid_kes": 1250000,
  "claims_count": 250,
  "loss_ratio": 0.33
}
```

### 17.2 Data Protection (Kenya Data Protection Act)

Requirements:

- Consent for data collection
- Right to access data
- Right to deletion
- Data breach notification (72 hours)
- Data Protection Impact Assessment (DPIA)

Compliance implementation:

```python
```
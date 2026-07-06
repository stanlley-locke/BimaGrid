# BimaGrid — Testing Guide

> Comprehensive testing reference covering all services, frameworks, and the full end-to-end parametric claim lifecycle.

---

## Test Architecture Overview

| Service | Framework | Test Types | Location |
|---|---|---|---|
| Django Backend | pytest + pytest-django | Unit, Integration, API, Celery | `backend/apps/*/tests/` |
| USSD Microservice | pytest | Unit, Integration, Session Flow | `ussd/tests/` |
| Smart Contracts | Hardhat (Mocha/Chai) | Unit, Integration, Gas | `contracts/test/` |
| gRPC Services | pytest + grpcio | Integration, Concurrent | `tests/test_grpc_services.py` |
| Oracle Node | Rust (cargo test) | Unit, Crypto | `oracle-node/src/**/*_test.rs` |
| API Gateway | Jest + curl | Unit, Rate Limit, Proxy | `api/gateway/tests/` |
| End-to-End | curl scripts | Full Lifecycle | `tests/e2e/` |

---

## 1. Backend Tests (Django / pytest)

### Setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements/base.txt -r requirements/test.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Run a specific app's tests
pytest apps/payments/ -v
pytest apps/policies/ -v
pytest apps/oracles/ -v

# Run a specific test file
pytest apps/payments/tests/test_mpesa.py -v

# Run tests matching a keyword
pytest -k "payout or claim" -v

# Stop at first failure
pytest -x

# Run with coverage report
pytest --cov=apps --cov-report=html --cov-report=term-missing

# Run parallel tests (faster)
pytest -n 4

# Show slowest tests
pytest --durations=10
```

### What's Covered

| App | Tests |
|---|---|
| `accounts` | Registration, JWT auth, profile update, phone verification |
| `policies` | Policy creation, H3 indexing, threshold validation, STK push |
| `claims` | Claim filing, parametric evaluation, status transitions |
| `payments` | M-Pesa STK push, B2C payout, callback processing, retry logic |
| `oracles` | Data submission, signature verification, consensus evaluation |
| `geospatial` | H3 index generation, ward lookup, coverage mapping |
| `pricing` | Premium calculation, crop risk constants, mitigation discounts |
| `satellite` | NASA POWER fetching, NDVI computation (mocked), data caching |
| `notifications` | SMS dispatch, celery task integration |
| `onboarding` | IPRS verification, ArdhiSasa lookup, step tracking |

### Environment for Testing

```bash
export DJANGO_SETTINGS_MODULE=config.settings.testing
export DATABASE_ENGINE=django.db.backends.sqlite3
export DATABASE_NAME=:memory:
export CELERY_TASK_ALWAYS_EAGER=True
export MPESA_USE_MOCK=True
export AFRICASTALKING_USE_MOCK=True
export OPENEO_USE_MOCK=True
export IPRS_USE_MOCK=True
```

---

## 2. USSD Microservice Tests (pytest)

```bash
cd ussd
source .venv/bin/activate

# All tests
pytest -v

# Test registration flow
pytest tests/test_registration_flow.py -v

# Test session routing
pytest tests/test_dispatcher.py -v

# Test Africa's Talking signature verification
pytest tests/test_gateway.py -v
```

### USSD Session Simulation

```bash
# Simulate a USSD session start (dial *384#)
curl -s -X POST http://localhost:8001/ussd/gateway/ \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'sessionId=ATsessionXYZ&serviceCode=%2A384%23&phoneNumber=%2B254711234567&text='

# Step 2 — select registration (option 1)
curl -s -X POST http://localhost:8001/ussd/gateway/ \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'sessionId=ATsessionXYZ&serviceCode=%2A384%23&phoneNumber=%2B254711234567&text=1'

# Step 3 — enter ward code
curl -s -X POST http://localhost:8001/ussd/gateway/ \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'sessionId=ATsessionXYZ&serviceCode=%2A384%23&phoneNumber=%2B254711234567&text=1*WARD-KISUMU-01'
```

Expected responses: `CON` (continue) or `END` (terminate).

---

## 3. Smart Contract Tests (Hardhat)

### Setup

```bash
cd contracts
npm install
```

### Running Tests

```bash
# All 25 tests
npx hardhat test

# With verbose Mocha output
npx hardhat test --verbose

# Filter by description
npx hardhat test --grep "payout"
npx hardhat test --grep "EscrowVault"

# Gas report (requires REPORT_GAS env var)
REPORT_GAS=true npx hardhat test

# Solidity coverage
npx hardhat coverage
```

### Test Summary (25 Tests)

| Suite | Tests | Description |
|---|---|---|
| `PolicyRegistry` | 6 | Registration, duplicate error, premium deposit, deactivation, zero-premium revert, zero-address revert |
| `Oracle Signature and Consensus` | 5 | Valid sig acceptance, unauthorized signer revert, duplicate revert, drought payout trigger, above-threshold no-payout |
| `EscrowVault` | 3 | Insufficient balance error, pull-payment refund claim, empty refund revert |
| `MitigationVerifier` | 3 | Cumulative discount, 50% cap, custom discount update |
| `Oracle Management` | 2 | Count tracking on add/remove, zero-address revert |
| `getMedian` | 6 | All orderings of 3 values + all-equal + large values |

### Gas Report Output (sample)

```
·---------------------------------------------|---------------------------|-------------|-----------------------------·
|         Solc version: 0.8.20                ·  Optimizer enabled: true  ·  Runs: 200  ·  Block limit: 30000000 gas  │
·············································|···························|·············|······························
|  Contract                                  ·  Method                   ·  Min        ·  Max        ·  Avg         │
·············································|···························|·············|·············|··············
|  KilimaShieldOracle                        ·  submitData               ·      92,145 ·     201,332 ·     132,540  │
|  KilimaShieldOracle                        ·  registerPolicy           ·     156,211 ·     156,211 ·     156,211  │
|  PolicyRegistry                            ·  registerPolicy           ·      91,334 ·      91,334 ·      91,334  │
|  EscrowVault                               ·  payout                   ·      42,100 ·      42,100 ·      42,100  │
|  EscrowVault                               ·  claimRefund              ·      38,902 ·      38,902 ·      38,902  │
·---------------------------------------------|---------------------------|-------------|-----------------------------·
```

---

## 4. gRPC Integration Tests (pytest)

```bash
# From project root
python3 -m pytest tests/test_grpc_services.py -v
```

### Test Coverage (13 Tests)

| Class | Test | Description |
|---|---|---|
| `TestOracleGrpc` | `test_submit_data_success` | Oracle data accepted and `success=True` returned |
| `TestOracleGrpc` | `test_submit_data_stored_by_servicer` | Submission stored in servicer's received list |
| `TestOracleGrpc` | `test_submit_data_multiple_oracles` | 3 independent oracles all return success |
| `TestUssdGrpc` | `test_register_farmer_success` | Farmer registered; policy number returned |
| `TestUssdGrpc` | `test_register_farmer_missing_fields_returns_error` | `INVALID_ARGUMENT` status code on empty phone |
| `TestUssdGrpc` | `test_get_policy_status_active` | Known phone returns `ACTIVE` status |
| `TestUssdGrpc` | `test_get_policy_status_not_found` | Unknown phone returns `NOT_FOUND` |
| `TestUssdGrpc` | `test_file_claim_all_peril_types[drought]` | Drought claim reference generated |
| `TestUssdGrpc` | `test_file_claim_all_peril_types[flood]` | Flood claim reference generated |
| `TestUssdGrpc` | `test_file_claim_all_peril_types[hail]` | Hail claim reference generated |
| `TestUssdGrpc` | `test_file_claim_all_peril_types[frost]` | Frost claim reference generated |
| `TestUssdGrpc` | `test_file_claim_invalid_loss_type` | `INVALID_ARGUMENT` for unknown peril |
| `TestUssdGrpc` | `test_concurrent_ussd_requests` | 10 simultaneous sessions — no errors, all 10 responses |

### Expected Output

```
============================= test session info ==============================
tests/test_grpc_services.py::TestOracleGrpc::test_submit_data_success PASSED
tests/test_grpc_services.py::TestOracleGrpc::test_submit_data_stored_by_servicer PASSED
tests/test_grpc_services.py::TestOracleGrpc::test_submit_data_multiple_oracles PASSED
tests/test_grpc_services.py::TestUssdGrpc::test_register_farmer_success PASSED
...
============================== 13 passed in 0.36s ==============================
```

---

## 5. Oracle Node Tests (Rust)

```bash
cd oracle-node

# Run all tests
cargo test

# With stdout output
cargo test -- --nocapture

# Run specific module
cargo test crypto
cargo test api

# Show test names
cargo test -- --list
```

### What's Tested

- **`crypto::mod`**: keccak256 hashing, EIP-191 signed message hash, ECDSA signature recovery consistency
- **`api::backend_client`**: HTTP payload serialization, retry logic
- **`api::grpc_client`**: gRPC request construction and connection lifecycle
- **`config::mod`**: TOML config parsing, env var override

---

## 6. API Gateway Health & Rate Limit Testing

### Health Check

```bash
curl -s http://localhost:3001/health | python3 -m json.tool
# {"status":"ok","version":"1.0.0","timestamp":"2026-07-06T04:40:00.000Z","uptime":3600.5}
```

### Rate Limit Test

```bash
# Fire 130 requests rapidly — 121st should return 429
for i in $(seq 1 130); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/api/v1/policies/)
  echo "Request $i: $STATUS"
done | grep "429" | head -5
```

### Proxy Validation

```bash
# Confirm /api/* routes to Django backend
curl -s -I http://localhost:3001/api/v1/auth/token/ | grep HTTP

# Confirm /ussd/* routes to USSD microservice
curl -s -I http://localhost:3001/ussd/health/ | grep HTTP
```

---

## 7. End-to-End Parametric Claim Lifecycle Test

This test walks through the complete flow from farmer registration to M-Pesa payout using only curl.

```bash
#!/bin/bash
# tests/e2e/full_lifecycle.sh
set -e

BASE="http://localhost:8000"
GW="http://localhost:3001"
echo "=== BimaGrid E2E Parametric Claim Test ==="

# ── Step 1: Register user ───────────────────────────────────
echo -e "\n[1] Registering farmer..."
REG=$(curl -s -X POST $BASE/api/v1/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"e2e@test.com","email":"e2e@test.com","password":"Test@1234","password_confirm":"Test@1234","first_name":"E2E","last_name":"Farmer","phone":"+254799000001"}')
echo "$REG" | python3 -m json.tool

# ── Step 2: Login ────────────────────────────────────────────
echo -e "\n[2] Logging in..."
AUTH=$(curl -s -X POST $BASE/api/v1/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"e2e@test.com","password":"Test@1234"}')
TOKEN=$(echo $AUTH | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")
echo "Token obtained: ${TOKEN:0:20}..."

# ── Step 3: Get premium quote ────────────────────────────────
echo -e "\n[3] Getting pricing quote..."
curl -s -X POST $BASE/api/v1/pricing/quote/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"crop":"MAIZE","acreage":2.5,"ward_code":"WARD-KISUMU-01","season":"LONG_RAINS_2026","mitigation_techniques":["drip_irrigation"]}' \
  | python3 -m json.tool

# ── Step 4: Create policy ────────────────────────────────────
echo -e "\n[4] Creating policy..."
POLICY=$(curl -s -X POST $BASE/api/v1/policies/ \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"crop":"MAIZE","acreage":2.5,"ward_code":"WARD-KISUMU-01","season":"LONG_RAINS_2026"}')
POLICY_ID=$(echo $POLICY | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Policy ID: $POLICY_ID"

# ── Step 5: Simulate M-Pesa callback (premium paid) ─────────
echo -e "\n[5] Simulating M-Pesa premium payment callback..."
curl -s -X POST $BASE/api/v1/payments/mpesa/callback/ \
  -H 'Content-Type: application/json' \
  -d "{\"Body\":{\"stkCallback\":{\"MerchantRequestID\":\"test-$POLICY_ID\",\"CheckoutRequestID\":\"ws_CO_e2e123\",\"ResultCode\":0,\"ResultDesc\":\"Success.\",\"CallbackMetadata\":{\"Item\":[{\"Name\":\"Amount\",\"Value\":1020.00},{\"Name\":\"MpesaReceiptNumber\",\"Value\":\"E2ETEST001\"},{\"Name\":\"PhoneNumber\",\"Value\":254799000001}]}}}}" \
  | python3 -m json.tool

# ── Step 6: Submit oracle data (3 oracles below threshold) ───
echo -e "\n[6] Submitting oracle data (simulating drought — below threshold)..."
for ORACLE_NUM in 1 2 3; do
  curl -s -X POST $BASE/api/v1/oracles/submit-data/ \
    -H 'Content-Type: application/json' \
    -H "X-Oracle-Signature: 0xsimulated_sig_$ORACLE_NUM" \
    -d "{
      \"oracle_id\": \"oracle-$ORACLE_NUM\",
      \"h3_index\": \"8928308280fffff\",
      \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
      \"rainfall_mm\": $((10 + ORACLE_NUM * 2)),
      \"ndvi\": 0.45,
      \"soil_moisture\": 0.20,
      \"data_sources\": [\"nasa-power\"]
    }" | python3 -m json.tool
done

# ── Step 7: Check policy status ──────────────────────────────
echo -e "\n[7] Checking policy payout status..."
sleep 2
curl -s $BASE/api/v1/policies/$POLICY_ID/status/ \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool

# ── Step 8: Check payout list ────────────────────────────────
echo -e "\n[8] Checking payout records..."
curl -s $BASE/api/v1/payments/payouts/ \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool

echo -e "\n=== E2E Test Complete ==="
```

Run the full lifecycle:
```bash
chmod +x tests/e2e/full_lifecycle.sh
bash tests/e2e/full_lifecycle.sh
```

---

## 8. Load Testing

### Using Apache Bench (ab)

```bash
# 1000 requests, 50 concurrent — health endpoint
ab -n 1000 -c 50 http://localhost:3001/health

# Rate limit stress test — should see 429 responses
ab -n 200 -c 20 -H "Content-Type: application/json" \
  http://localhost:3001/api/v1/policies/
```

### Using siege

```bash
# Install: sudo apt install siege
# Sustained load for 60 seconds, 25 concurrent users
siege -c 25 -t 60s http://localhost:3001/health

# Test specific endpoints from a URL file
cat > urls.txt <<EOF
http://localhost:8000/api/v1/policies/
http://localhost:8000/health/
http://localhost:3001/health
EOF
siege -c 10 -t 30s -f urls.txt
```

### Using k6

```bash
# Install: https://k6.io/docs/getting-started/installation/
k6 run - <<'EOF'
import http from 'k6/http';
import { check } from 'k6';
export const options = { vus: 20, duration: '30s' };
export default function () {
  const r = http.get('http://localhost:3001/health');
  check(r, { 'status is 200': (r) => r.status === 200 });
}
EOF
```

---

## 9. CI/CD Pipeline (GitHub Actions)

The CI pipeline runs on every push to `main` and `develop`, and all PRs targeting `main`.

**Workflow file:** `.github/workflows/ci.yml`

### Pipeline Jobs

```
push/PR
  │
  ├── test-backend      Python 3.12 + PostgreSQL 16 + Redis 7
  │     └── pytest with coverage → Codecov
  │
  ├── test-ussd         Python 3.12 standalone
  │     └── pytest
  │
  ├── test-grpc         Python 3.12 + grpcio-tools
  │     └── generate stubs → pytest test_grpc_services.py
  │
  ├── test-contracts    Node.js 20
  │     └── npx hardhat compile → npx hardhat test → gas report
  │
  ├── test-oracle       Rust 1.78 + protobuf-compiler
  │     └── cargo test
  │
  └── build-and-push    (main branch only, after all tests pass)
        ├── Build backend Docker image → ghcr.io
        ├── Build USSD Docker image → ghcr.io
        └── Build API Gateway image → ghcr.io
```

### Trigger CI Locally

```bash
# Simulate the full test suite locally before pushing
pytest backend/          # Backend
pytest ussd/             # USSD
python3 -m pytest tests/test_grpc_services.py  # gRPC
cd contracts && npx hardhat test               # Contracts
cd oracle-node && cargo test                   # Oracle
```

---

## 10. Useful Testing Utilities

```bash
# Watch test files and auto-rerun on change (pytest-watch)
pip install pytest-watch
ptw backend/apps/payments/

# Run only tests that failed last time
pytest --lf

# Run tests in random order (catch order dependencies)
pip install pytest-randomly
pytest --randomly-seed=12345

# Profile slow tests
pytest --durations=10 backend/

# Check import times
python -X importtime -c "import django; django.setup()"

# Solidity static analysis (Slither)
pip install slither-analyzer
cd contracts && slither .

# Check contract ABI for breaking changes
diff contracts/abi/KilimaShieldOracle.json contracts/abi/KilimaShieldOracle.prev.json
```

# BimaGrid — Getting Started Guide

> **Complete development setup guide for all BimaGrid services**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start with Docker](#quick-start-with-docker)
3. [Manual Development Setup](#manual-development-setup)
4. [Environment Configuration](#environment-configuration)
5. [Running Tests](#running-tests)
6. [gRPC Development](#grpc-development)
7. [Useful Commands](#useful-commands)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Ensure all tools are installed before proceeding.

| Tool | Minimum Version | Install Link |
|------|----------------|-------------|
| **Git** | 2.40+ | https://git-scm.com/downloads |
| **Python** | 3.12+ | https://www.python.org/downloads/ |
| **Node.js** | 20 LTS | https://nodejs.org/en/download |
| **npm** | 10+ | Bundled with Node.js |
| **Rust** | 1.78 stable | https://rustup.rs/ |
| **Cargo** | 1.78+ | Bundled with Rust |
| **Docker** | 26+ | https://docs.docker.com/get-docker/ |
| **Docker Compose** | 2.27+ | https://docs.docker.com/compose/install/ |
| **PostgreSQL** | 16+ | https://www.postgresql.org/download/ |
| **Redis** | 7.2+ | https://redis.io/download |
| **grpcurl** | latest | https://github.com/fullstorydev/grpcurl/releases |
| **Hardhat (via npm)** | 2.22+ | Installed via `npm install` in contracts/ |
| **protoc** | 25+ | https://github.com/protocolbuffers/protobuf/releases |

### Verify installations

```bash
git --version          # git version 2.43.0
python3 --version      # Python 3.12.x
node --version         # v20.x.x
npm --version          # 10.x.x
rustc --version        # rustc 1.78.0
cargo --version        # cargo 1.78.0
docker --version       # Docker version 26.x
docker compose version # Docker Compose version v2.27.x
```

---

## Quick Start with Docker

The fastest way to run all BimaGrid services locally.

```bash
# 1. Clone the repository
git clone https://github.com/your-org/BimaGrid.git && cd BimaGrid

# 2. Copy environment file and fill in your values
cp .env.example .env

# 3. Build all Docker images
docker compose build

# 4. Start all services (detached)
docker compose up -d

# 5. Run database migrations
docker compose exec backend python manage.py migrate
docker compose exec ussd python manage.py migrate
```

After startup, services are available at:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend REST API | http://localhost:8000/api/v1/ |
| Django Admin | http://localhost:8000/admin/ |
| API Gateway | http://localhost:3001/api/ |
| USSD Microservice | http://localhost:8001/ |
| gRPC Server | localhost:50051 |
| Celery Flower | http://localhost:5555 |

---

## Manual Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/BimaGrid.git
cd BimaGrid
```

### 2. Copy Environment File

```bash
cp .env.example .env
# Edit .env with your local credentials
nano .env
```

---

### 3. Backend (Django REST + gRPC) — Port 8000 / 50051

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements/base.txt
pip install -r requirements/dev.txt

# Set environment variables (or ensure .env is loaded)
export DJANGO_SETTINGS_MODULE=bimagrid.settings.development

# Run database migrations
python manage.py migrate

# Create admin superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --no-input

# Start Django development server (REST API on port 8000)
python manage.py runserver 0.0.0.0:8000

# In a separate terminal: start gRPC server on port 50051
python manage.py grpcserver --port 50051

# In a separate terminal: start Celery worker
celery -A bimagrid worker --loglevel=info

# In a separate terminal: start Celery Beat scheduler
celery -A bimagrid beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

### 4. USSD Microservice — Port 8001

```bash
cd ussd

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set environment variables
export DJANGO_SETTINGS_MODULE=ussd_service.settings
export BACKEND_GRPC_HOST=localhost
export BACKEND_GRPC_PORT=50051

# Run database migrations
python manage.py migrate

# Start USSD service on port 8001
python manage.py runserver 0.0.0.0:8001
```

The USSD service expects incoming POST requests from Africa's Talking at:
`POST http://localhost:8001/ussd/callback/`

Configure your Africa's Talking sandbox callback URL to point here (use ngrok for local development):
```bash
ngrok http 8001
# Then set callback URL in Africa's Talking dashboard to:
# https://<ngrok-id>.ngrok.io/ussd/callback/
```

---

### 5. Smart Contracts (Solidity / Hardhat)

```bash
cd contracts

# Install Node.js dependencies
npm install

# Start local Hardhat node (separate terminal, keeps running)
npx hardhat node
# Local RPC: http://localhost:8545
# Chain ID: 31337

# Compile contracts
npx hardhat compile

# Deploy contracts to local Hardhat node
npx hardhat run scripts/deploy.ts --network localhost

# The deployment script outputs contract addresses — copy them to .env:
# KILIMA_SHIELD_ORACLE_ADDRESS=0x...
# POLICY_REGISTRY_ADDRESS=0x...
# ESCROW_VAULT_ADDRESS=0x...
# MITIGATION_VERIFIER_ADDRESS=0x...
```

---

### 6. Oracle Node (Rust / tokio / tonic)

```bash
cd oracle-node

# Ensure Rust stable is active
rustup default stable
rustup update stable

# Build in debug mode (faster compilation)
cargo build

# Configure environment (copy and edit)
cp .env.example .env
# Set ORACLE_PRIVATE_KEY, BACKEND_GRPC_HOST, NASA_POWER_API_KEY, etc.

# Run oracle node
cargo run

# Or run with release optimizations
cargo run --release
```

The oracle node will:
1. Connect to the gRPC backend at `BACKEND_GRPC_HOST:BACKEND_GRPC_PORT`
2. Call `GetActivePolicyCells` to fetch monitored H3 cells
3. Fetch satellite data from NASA POWER / CHIRPS / openEO APIs
4. Evaluate thresholds and sign data with secp256k1
5. Submit via `SubmitOracleData` gRPC call every `ORACLE_POLL_INTERVAL_SECS`

---

### 7. Frontend (React / Next.js) — Port 3000

```bash
cd frontend

# Install dependencies
npm install

# Set up environment
cp .env.local.example .env.local
# Edit .env.local with API gateway URL, Mapbox token, etc.

# Start development server
npm run dev
# Available at http://localhost:3000

# Type check
npx tsc --noEmit

# Build for production
npm run build
```

---

### 8. API Gateway (Node.js / TypeScript / Express) — Port 3001

```bash
cd gateway

# Install dependencies
npm install

# Set up environment
cp .env.example .env

# Start development server with hot reload
npm run dev
# Available at http://localhost:3001

# Type check
npx tsc --noEmit

# Build production bundle
npm run build
npm run start
```

---

## Environment Configuration

Copy `.env.example` to `.env` and set the following variables. Variables marked **required** must be set for the service to start; **optional** variables have defaults.

### Core / Shared

| Variable | Required | Description | Example Value |
|----------|----------|-------------|---------------|
| `DJANGO_SECRET_KEY` | ✅ | Django secret key for cryptographic signing | `django-insecure-50-char-random-string` |
| `DJANGO_DEBUG` | ✅ | Enable Django debug mode | `True` (dev) / `False` (prod) |
| `DJANGO_ALLOWED_HOSTS` | ✅ | Comma-separated allowed hostnames | `localhost,127.0.0.1,api.bimagrid.io` |
| `DJANGO_SETTINGS_MODULE` | ✅ | Settings module to use | `bimagrid.settings.development` |
| `ENVIRONMENT` | ✅ | Current environment | `development` / `staging` / `production` |

### Database

| Variable | Required | Description | Example Value |
|----------|----------|-------------|---------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection URL | `postgresql://bimagrid_user:password@localhost:5432/bimagrid` |
| `DB_HOST` | ✅ | PostgreSQL host | `localhost` |
| `DB_PORT` | ✅ | PostgreSQL port | `5432` |
| `DB_NAME` | ✅ | Database name | `bimagrid` |
| `DB_USER` | ✅ | Database user | `bimagrid_user` |
| `DB_PASSWORD` | ✅ | Database password | `supersecretpassword` |

### Redis / Celery

| Variable | Required | Description | Example Value |
|----------|----------|-------------|---------------|
| `REDIS_URL` | ✅ | Redis connection URL | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | ✅ | Celery broker URL | `redis://localhost:6379/1` |
| `CELERY_RESULT_BACKEND` | ✅ | Celery result backend | `redis://localhost:6379/2` |

### JWT Authentication

| Variable | Required | Description | Example Value |
|----------|----------|-------------|---------------|
| `JWT_SECRET_KEY` | ✅ | JWT signing secret | `your-jwt-secret-key-256-bits` |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | ❌ | Access token TTL | `15` |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | ❌ | Refresh token TTL | `7` |

### gRPC

| Variable | Required | Description | Example Value |
|----------|----------|-------------|---------------|
| `GRPC_HOST` | ✅ | gRPC server host | `0.0.0.0` |
| `GRPC_PORT` | ✅ | gRPC server port | `50051` |
| `BACKEND_GRPC_HOST` | ✅ | Backend gRPC host (for USSD/Oracle) | `localhost` |
| `BACKEND_GRPC_PORT` | ✅ | Backend gRPC port (for USSD/Oracle) | `50051` |

### M-Pesa Daraja

| Variable | Required | Description | Example Value |
|----------|----------|-------------|---------------|
| `MPESA_CONSUMER_KEY` | ✅ | Daraja API consumer key | `your-consumer-key` |
| `MPESA_CONSUMER_SECRET` | ✅ | Daraja API consumer secret | `your-consumer-secret` |
| `MPESA_SHORTCODE` | ✅ | M-Pesa paybill/till number | `174379` |
| `MPESA_PASSKEY` | ✅ | STK Push passkey | `bfb279f9aa9bdbcf158e97dd71a467...` |
| `MPESA_B2C_INITIATOR_NAME` | ✅ | B2C initiator username | `testapi` |
| `MPESA_B2C_INITIATOR_PASSWORD` | ✅ | B2C initiator password | `Safaricom999!` |
| `MPESA_CALLBACK_URL` | ✅ | STK Push callback URL | `https://api.bimagrid.io/api/v1/payments/mpesa/callback/` |
| `MPESA_B2C_RESULT_URL` | ✅ | B2C result callback URL | `https://api.bimagrid.io/api/v1/payments/mpesa/b2c/result/` |
| `MPESA_ENVIRONMENT` | ✅ | API environment | `sandbox` / `production` |

### Blockchain / Smart Contracts

| Variable | Required | Description | Example Value |
|----------|----------|-------------|---------------|
| `RPC_URL` | ✅ | Blockchain RPC endpoint | `http://localhost:8545` (dev) |
| `CHAIN_ID` | ✅ | Blockchain chain ID | `31337` (Hardhat) / `44787` (Alfajores) / `42220` (Celo) |
| `KILIMA_SHIELD_ORACLE_ADDRESS` | ✅ | Deployed oracle contract address | `0x5FbDB2315678afecb367f032d93F642f64180aa3` |
| `POLICY_REGISTRY_ADDRESS` | ✅ | Deployed registry contract address | `0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512` |
| `ESCROW_VAULT_ADDRESS` | ✅ | Deployed escrow contract address | `0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0` |
| `MITIGATION_VERIFIER_ADDRESS` | ✅ | Deployed verifier contract address | `0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9` |
| `BACKEND_WALLET_PRIVATE_KEY` | ✅ | Backend wallet for contract interactions | `0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80` |

### Oracle Node (Rust)

| Variable | Required | Description | Example Value |
|----------|----------|-------------|---------------|
| `ORACLE_PRIVATE_KEY` | ✅ | secp256k1 private key for signing | `0x59c6995e998f97a5a0044966f094538...` |
| `ORACLE_POLL_INTERVAL_SECS` | ❌ | How often to poll satellite APIs | `21600` (6 hours) |
| `NASA_POWER_API_KEY` | ✅ | NASA POWER API key | `your-nasa-api-key` |
| `NASA_POWER_BASE_URL` | ❌ | NASA POWER API base URL | `https://power.larc.nasa.gov/api` |
| `CHIRPS_BASE_URL` | ❌ | CHIRPS data base URL | `https://data.chc.ucsb.edu/products/CHIRPS-2.0` |
| `OPENEO_BASE_URL` | ✅ | openEO backend URL | `https://openeo.cloud` |
| `OPENEO_CLIENT_ID` | ✅ | openEO client ID | `your-openeo-client-id` |
| `OPENEO_CLIENT_SECRET` | ✅ | openEO client secret | `your-openeo-secret` |
| `MOCK_SATELLITE_DATA` | ❌ | Use mock data instead of real APIs | `true` (dev) / `false` (prod) |

### Africa's Talking (USSD + SMS)

| Variable | Required | Description | Example Value |
|----------|----------|-------------|---------------|
| `AT_API_KEY` | ✅ | Africa's Talking API key | `atsk_xxxxxxxxxxxxxxxx` |
| `AT_USERNAME` | ✅ | Africa's Talking username | `sandbox` (dev) / `bimagrid` (prod) |
| `AT_USSD_CODE` | ✅ | USSD shortcode | `*384#` |
| `AT_SENDER_ID` | ❌ | SMS sender ID | `BimaGrid` |

### Frontend

| Variable | Required | Description | Example Value |
|----------|----------|-------------|---------------|
| `NEXT_PUBLIC_API_URL` | ✅ | API gateway base URL | `http://localhost:3001/api` |
| `NEXT_PUBLIC_MAPBOX_TOKEN` | ✅ | Mapbox GL JS access token | `pk.eyJ1IjoiYmltYWdyaWQiLCJh...` |
| `NEXT_PUBLIC_CHAIN_ID` | ✅ | Blockchain chain ID | `31337` |

### API Gateway

| Variable | Required | Description | Example Value |
|----------|----------|-------------|---------------|
| `BACKEND_URL` | ✅ | Django backend URL | `http://localhost:8000` |
| `GATEWAY_PORT` | ❌ | Gateway listen port | `3001` |
| `RATE_LIMIT_WINDOW_MS` | ❌ | Rate limit window in ms | `60000` |
| `RATE_LIMIT_MAX_REQUESTS` | ❌ | Max requests per window | `100` |
| `JWT_PUBLIC_KEY` | ✅ | JWT public key for verification | `-----BEGIN PUBLIC KEY-----...` |

---

## Running Tests

### Backend Tests (pytest)

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_policies.py -v

# Run specific test by name
pytest tests/test_policies.py::TestPolicyViewSet::test_create_policy -v

# Run tests with specific markers
pytest -m "integration" -v
pytest -m "not slow" -v

# Run with parallel workers (requires pytest-xdist)
pytest -n auto

# Run and output to XML for CI
pytest --junitxml=test-results.xml
```

Key test modules:
- `tests/test_auth.py` — JWT auth, registration, token refresh
- `tests/test_policies.py` — Policy CRUD, status transitions
- `tests/test_claims.py` — Claim creation, threshold evaluation
- `tests/test_payments.py` — M-Pesa STK Push, B2C callback handling
- `tests/test_oracle.py` — Oracle data ingestion, signature verification
- `tests/test_geospatial.py` — H3 indexing, GPS to cell conversion
- `tests/test_grpc_services.py` — gRPC service integration tests

### USSD Tests (pytest)

```bash
cd ussd
source venv/bin/activate

# Run all USSD tests
pytest

# Run with coverage
pytest --cov=ussd_service --cov-report=term-missing -v

# Test specific USSD flow
pytest tests/test_ussd_flows.py::TestRegistrationFlow -v
pytest tests/test_ussd_flows.py::TestPolicyPurchaseFlow -v
pytest tests/test_ussd_flows.py::TestClaimFlow -v

# Test gRPC client calls
pytest tests/test_grpc_client.py -v
```

Key test modules:
- `tests/test_ussd_flows.py` — Full USSD menu navigation simulation
- `tests/test_grpc_client.py` — gRPC stub calls to backend
- `tests/test_session_management.py` — USSD session state machine

### Smart Contract Tests (Hardhat)

```bash
cd contracts

# Run all Hardhat tests
npx hardhat test

# Run with gas usage report
REPORT_GAS=true npx hardhat test

# Run specific test file
npx hardhat test test/KilimaShieldOracle.test.ts
npx hardhat test test/PolicyRegistry.test.ts
npx hardhat test test/EscrowVault.test.ts
npx hardhat test test/MitigationVerifier.test.ts

# Run with verbose output
npx hardhat test --verbose

# Generate coverage report (requires solidity-coverage)
npx hardhat coverage

# Check contract sizes
npx hardhat size-contracts
```

Key test files:
- `test/KilimaShieldOracle.test.ts` — Oracle registration, signature verification, threshold breach
- `test/PolicyRegistry.test.ts` — Policy creation, access control, H3 indexing
- `test/EscrowVault.test.ts` — Premium locking, payout authorization, reentrancy protection
- `test/MitigationVerifier.test.ts` — Merkle proof verification, mitigation records

### gRPC Integration Tests

```bash
cd backend
source venv/bin/activate

# Run gRPC-specific integration tests
python3 -m pytest tests/test_grpc_services.py -v

# Test OracleService methods
python3 -m pytest tests/test_grpc_services.py::TestOracleService -v

# Test UssdService methods
python3 -m pytest tests/test_grpc_services.py::TestUssdService -v

# Test with gRPC server running (requires backend to be up)
python3 -m pytest tests/test_grpc_services.py -v --grpc-host=localhost --grpc-port=50051
```

### Oracle Node Tests (Rust / cargo)

```bash
cd oracle-node

# Run all unit and integration tests
cargo test

# Run with output (print statements visible)
cargo test -- --nocapture

# Run specific test module
cargo test satellite_fetcher::tests

# Run specific test function
cargo test test_h3_cell_conversion

# Run with release optimizations
cargo test --release

# Run with code coverage (requires cargo-tarpaulin)
cargo tarpaulin --out Html

# Check for common issues
cargo clippy --all-targets --all-features
```

Key test modules:
- `src/satellite/tests.rs` — NASA POWER / CHIRPS / openEO fetch mocks
- `src/signing/tests.rs` — secp256k1 key generation, signing, verification
- `src/grpc/tests.rs` — gRPC client connection and retry logic
- `src/h3/tests.rs` — H3 cell resolution, GPS conversion, bytes32 packing

### API Gateway Tests

```bash
cd gateway

# Check gateway is healthy
curl -s http://localhost:3001/health | jq .

# Run Jest unit tests
npm test

# Run with coverage
npm test -- --coverage

# Test rate limiting (should return 429 after 100 requests/min)
for i in $(seq 1 110); do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3001/api/v1/health/
done

# Type check without compiling
npx tsc --noEmit
```

---

## gRPC Development

### Regenerate Python Stubs from Proto

```bash
# From project root
chmod +x scripts/generate_grpc.sh
./scripts/generate_grpc.sh

# Or manually:
cd proto
python -m grpc_tools.protoc \
  -I. \
  --python_out=../backend/bimagrid/grpc_services/generated \
  --grpc_python_out=../backend/bimagrid/grpc_services/generated \
  --python_out=../ussd/ussd_service/grpc_client/generated \
  --grpc_python_out=../ussd/ussd_service/grpc_client/generated \
  bimagrid.proto
```

### Regenerate Rust Stubs from Proto

Tonic builds are configured in `oracle-node/build.rs`. Stubs regenerate automatically on `cargo build`:

```bash
cd oracle-node
cargo build
# build.rs runs tonic-build::compile_protos("../proto/bimagrid.proto")
```

### Start gRPC Server for Testing

```bash
cd backend
source venv/bin/activate
python manage.py grpcserver --port 50051
```

### Test gRPC with grpcurl

```bash
# List all available services
grpcurl -plaintext localhost:50051 list

# Describe a service
grpcurl -plaintext localhost:50051 describe bimagrid.OracleService

# Call SubmitOracleData
grpcurl -plaintext \
  -d '{
    "h3_cells": ["8928308280fffff"],
    "rainfall_mm": 38.5,
    "ndvi_score": 0.42,
    "evapotranspiration": 5.2,
    "timestamp": 1717200000,
    "oracle_pubkey": "02abc123..."
  }' \
  localhost:50051 bimagrid.OracleService/SubmitOracleData

# Call GetActivePolicyCells
grpcurl -plaintext \
  -d '{"active_only": true}' \
  localhost:50051 bimagrid.OracleService/GetActivePolicyCells

# Call UssdService.GetPolicyStatus
grpcurl -plaintext \
  -d '{"farmer_phone": "+254712345678"}' \
  localhost:50051 bimagrid.UssdService/GetPolicyStatus

# Health check (requires grpc.health.v1.Health)
grpcurl -plaintext localhost:50051 grpc.health.v1.Health/Check
```

---

## Useful Commands

| Task | Command |
|------|---------|
| **Start all services (Docker)** | `docker compose up -d` |
| **Stop all services** | `docker compose down` |
| **View all service logs** | `docker compose logs -f` |
| **View specific service logs** | `docker compose logs -f backend` |
| **Backend shell** | `docker compose exec backend python manage.py shell` |
| **Run migrations** | `docker compose exec backend python manage.py migrate` |
| **Create superuser** | `docker compose exec backend python manage.py createsuperuser` |
| **Restart single service** | `docker compose restart backend` |
| **Rebuild single service** | `docker compose build backend && docker compose up -d backend` |
| **Django DB shell** | `docker compose exec backend python manage.py dbshell` |
| **PostgreSQL CLI** | `psql -h localhost -U bimagrid_user -d bimagrid` |
| **Redis CLI** | `redis-cli -h localhost ping` |
| **Flush Redis cache** | `redis-cli -h localhost FLUSHDB` |
| **Celery worker status** | `docker compose exec celery celery -A bimagrid inspect active` |
| **Purge Celery queue** | `docker compose exec celery celery -A bimagrid purge` |
| **Contract compilation** | `cd contracts && npx hardhat compile` |
| **Contract deployment (local)** | `cd contracts && npx hardhat run scripts/deploy.ts --network localhost` |
| **Format Python code** | `cd backend && black . && isort .` |
| **Lint Python code** | `cd backend && flake8 .` |
| **Format Rust code** | `cd oracle-node && cargo fmt` |
| **Lint Rust code** | `cd oracle-node && cargo clippy` |
| **Format TypeScript** | `cd frontend && npx prettier --write .` |
| **Generate proto docs** | `protoc --doc_out=docs/ --doc_opt=markdown,proto.md proto/bimagrid.proto` |

---

## Troubleshooting

### `django.db.utils.OperationalError: could not connect to server`

**Cause**: PostgreSQL is not running or `DATABASE_URL` is incorrect.

```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Start PostgreSQL (Linux systemd)
sudo systemctl start postgresql

# Docker: check postgres container
docker compose ps postgres
docker compose logs postgres

# Verify DATABASE_URL in .env
echo $DATABASE_URL
```

---

### `redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379`

**Cause**: Redis is not running.

```bash
# Check Redis
redis-cli ping

# Start Redis (Linux)
sudo systemctl start redis

# Docker: check redis container
docker compose ps redis
docker compose logs redis
```

---

### `ModuleNotFoundError: No module named 'bimagrid_pb2'`

**Cause**: gRPC Python stubs have not been generated.

```bash
# Regenerate stubs
./scripts/generate_grpc.sh

# Or manually
pip install grpcio-tools
python -m grpc_tools.protoc -I./proto --python_out=./backend --grpc_python_out=./backend ./proto/bimagrid.proto
```

---

### `Error: Cannot find module '@/components/...'`

**Cause**: Frontend dependencies not installed or tsconfig paths misconfigured.

```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

---

### `error[E0433]: failed to resolve: use of undeclared crate or module`

**Cause**: Rust dependencies not downloaded.

```bash
cd oracle-node
cargo clean
cargo build
```

---

### Oracle Node: `Error: ORACLE_PRIVATE_KEY is not set`

**Cause**: Missing environment variable.

```bash
# Generate a new secp256k1 private key for development
cd oracle-node
cargo run --example generate_keypair
# Outputs: Private key: 0x... | Public key: 02...
# Add to .env: ORACLE_PRIVATE_KEY=0x...
```

---

### `hardhat: command not found`

**Cause**: Hardhat not installed or not in PATH.

```bash
cd contracts
npm install
npx hardhat --version
# Use npx hardhat (not hardhat directly)
```

---

### M-Pesa STK Push returns `Invalid Access Token`

**Cause**: Daraja credentials incorrect or token expired.

```bash
# Manually test token generation
curl -u "$MPESA_CONSUMER_KEY:$MPESA_CONSUMER_SECRET" \
  https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials

# Ensure MPESA_ENVIRONMENT=sandbox for development
# Ensure callback URL is publicly accessible (use ngrok for local dev)
ngrok http 8000
```

---

### Port already in use

```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>

# Or use fuser
fuser -k 8000/tcp
```

---

### Docker: `no space left on device`

```bash
# Clean up unused Docker resources
docker system prune -af --volumes

# Check disk usage
docker system df
```

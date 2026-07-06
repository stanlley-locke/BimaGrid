# BimaGrid — Project Startup & Installation Guide

> Get the full BimaGrid stack running locally in minutes.

---

## Prerequisites

| Tool | Minimum Version | Install |
|---|---|---|
| Docker + Docker Compose | 24.0 / 2.20 | https://docs.docker.com/get-docker/ |
| Python | 3.12 | https://www.python.org/downloads/ |
| Node.js | 20 LTS | https://nodejs.org/ |
| Rust toolchain | 1.78 | https://rustup.rs/ |
| Git | 2.40 | https://git-scm.com/ |
| protobuf-compiler | 3.x | `apt install protobuf-compiler` / `brew install protobuf` |
| grpcurl (optional) | latest | https://github.com/fullstorydev/grpcurl |

---

## Quick Start — Docker (Recommended)

Get everything running in 5 commands:

```bash
# 1. Clone the repository
git clone https://github.com/your-org/BimaGrid.git && cd BimaGrid

# 2. Configure environment
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY and POSTGRES_PASSWORD

# 3. Generate gRPC Python stubs
bash scripts/generate_grpc.sh

# 4. Start all services (postgres, redis, backend, ussd, celery, oracle, frontend, nginx, hardhat)
docker compose up -d

# 5. Apply migrations and create superuser
docker compose exec backend python manage.py migrate --noinput
docker compose exec backend python manage.py createsuperuser
```

**Services available at:**
| Service | URL |
|---|---|
| Django REST API | http://localhost:8000/api/ |
| Django Admin | http://localhost:8000/admin/ |
| API Gateway | http://localhost:3001 |
| Frontend | http://localhost:3000 |
| USSD Microservice | http://localhost:8001 |
| gRPC Server | localhost:50051 |
| Hardhat Node | http://localhost:8545 |
| Nginx (main entry) | http://localhost:80 |

---

## Manual Development Setup

### 1. Clone & Configure

```bash
git clone https://github.com/your-org/BimaGrid.git
cd BimaGrid
cp .env.example .env
```

Open `.env` and fill in the required values (see [Environment Configuration](#environment-configuration) below).

---

### 2. Django Backend (Python)

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements/base.txt
pip install -r requirements/test.txt   # for running tests

# Apply database migrations
python manage.py migrate --noinput

# Load initial fixtures (pricing rules, crop data)
python manage.py loaddata fixtures/initial_pricing_rules.json

# Create a superuser
python manage.py createsuperuser

# Generate Swahili/English translations
python manage.py compilemessages

# Collect static files
python manage.py collectstatic --noinput

# Start the development server
python manage.py runserver 0.0.0.0:8000

# In a separate terminal — start the gRPC server
python manage.py run_grpc_server     # listens on port 50051

# In another terminal — start Celery worker
celery -A config worker -l INFO -Q default,payouts,notifications

# Celery beat scheduler (yet another terminal)
celery -A config beat -l INFO
```

---

### 3. USSD Microservice (Python)

```bash
cd ussd

python -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements/base.txt

python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8001
```

Make sure `BACKEND_URL=http://localhost:8000` and `GRPC_BACKEND_TARGET=localhost:50051` are set in `.env`.

---

### 4. Smart Contracts (Hardhat)

```bash
cd contracts

npm install

# Start local Hardhat Ethereum node (keep this terminal open)
npx hardhat node

# In a new terminal — deploy contracts to local node
npx hardhat run scripts/deploy.ts --network localhost

# Run tests
npx hardhat test

# Gas report
REPORT_GAS=true npx hardhat test
```

After deployment, copy the printed contract addresses into your `.env`:
```
CONTRACT_KILIMA_SHIELD_ORACLE=0x...
CONTRACT_POLICY_REGISTRY=0x...
CONTRACT_ESCROW_VAULT=0x...
```

---

### 5. Oracle Node (Rust)

```bash
cd oracle-node

# Install protobuf compiler (required for tonic build.rs)
# Ubuntu:  sudo apt install protobuf-compiler
# macOS:   brew install protobuf

# Edit oracle config
cp oracle-config-1.toml.example oracle-config-1.toml
# Set signing_key, contract_address, backend_url

# Build and run
cargo run -- --config oracle-config-1.toml

# Or run in release mode
cargo build --release
./target/release/bimagrid-oracle --config oracle-config-1.toml
```

---

### 6. API Gateway (Node.js/TypeScript)

```bash
cd api/gateway

npm install

# Development (hot-reload)
npm run dev

# Production build
npm run build
npm start
```

Gateway runs on port `3001` and proxies:
- `http://localhost:3001/api/*` → Django Backend
- `http://localhost:3001/ussd/*` → USSD Microservice

---

### 7. Frontend (Next.js)

```bash
cd frontend

npm install

# Development server
npm run dev     # http://localhost:3000

# Production build
npm run build
npm start
```

---

### 8. Generate gRPC Stubs

Run this whenever `protos/bimagrid.proto` changes:

```bash
# From project root
bash scripts/generate_grpc.sh

# This generates:
#   backend/apps/grpc_services/bimagrid_pb2.py
#   backend/apps/grpc_services/bimagrid_pb2_grpc.py
#   ussd/src/grpc_services/bimagrid_pb2.py
#   ussd/src/grpc_services/bimagrid_pb2_grpc.py
#   (Rust stubs via cargo build + build.rs automatically)
```

---

## Environment Configuration

Copy `.env.example` to `.env` and configure all variables:

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Django secret key | `django-insecure-abc123...` |
| `DEBUG` | Django debug mode | `True` (dev) / `False` (prod) |
| `ALLOWED_HOSTS` | Comma-separated hostnames | `localhost,127.0.0.1` |
| `DATABASE_ENGINE` | Django DB backend | `django.db.backends.postgresql` |
| `DATABASE_NAME` | Database name | `bimagrid` |
| `DATABASE_USER` | Database user | `bimagrid` |
| `DATABASE_PASSWORD` | Database password | `strongpassword` |
| `DATABASE_HOST` | Database host | `localhost` (Docker: `postgres`) |
| `POSTGRES_DB` | Docker Compose Postgres DB | `bimagrid` |
| `POSTGRES_PASSWORD` | Docker Compose Postgres password | `strongpassword` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | Celery broker | `redis://localhost:6379/0` |
| `MPESA_CONSUMER_KEY` | M-Pesa Daraja app key | From Safaricom portal |
| `MPESA_CONSUMER_SECRET` | M-Pesa Daraja secret | From Safaricom portal |
| `MPESA_SHORTCODE` | M-Pesa shortcode | `174379` (sandbox) |
| `MPESA_PASSKEY` | M-Pesa STK passkey | From Safaricom portal |
| `MPESA_USE_MOCK` | Use mock M-Pesa | `True` (dev) |
| `AFRICASTALKING_USERNAME` | AT username | `sandbox` |
| `AFRICASTALKING_API_KEY` | AT API key | From AT dashboard |
| `AFRICASTALKING_USE_MOCK` | Use mock AT | `True` (dev) |
| `BACKEND_URL` | Backend URL for USSD service | `http://localhost:8000` |
| `GRPC_BACKEND_TARGET` | gRPC target for USSD→Backend | `localhost:50051` |
| `BLOCKCHAIN_RPC_URL` | Ethereum RPC endpoint | `http://localhost:8545` |
| `ORACLE_SIGNING_KEY` | Oracle secp256k1 private key | `0x47e175...` |
| `ORACLE_AUTHORIZED_KEYS` | Authorized oracle addresses | `0xAbc...,0xDef...` |
| `CONTRACT_KILIMA_SHIELD_ORACLE` | Deployed oracle contract | `0x5FbD...` |
| `OPENEO_BACKEND_URL` | openEO API endpoint | `https://earthengine.openeo.org` |
| `OPENEO_USE_MOCK` | Use mock satellite data | `True` (dev) |
| `IPRS_USE_MOCK` | Use mock IPRS | `True` (dev) |
| `ARDHISASA_USE_MOCK` | Use mock land registry | `True` (dev) |
| `NEXT_PUBLIC_API_URL` | Frontend API base URL | `http://localhost:3001/api` |
| `NEXT_PUBLIC_CHAIN_ID` | Blockchain chain ID | `31337` (Hardhat) |
| `INTERNAL_API_KEY` | Internal service-to-service key | `bimagrid-internal-dev-key` |

---

## Running Tests

### Backend (pytest)

```bash
cd backend
pytest                                    # all tests
pytest -v                                  # verbose
pytest apps/payments/ -v                  # specific app
pytest --cov=apps --cov-report=html       # with HTML coverage
pytest -k "test_payout" -v               # filter by name
pytest --tb=short -q                      # compact output
```

### USSD Microservice (pytest)

```bash
cd ussd
pytest -v
pytest tests/test_gateway.py -v
```

### gRPC Integration Tests (pytest)

```bash
# From project root
python3 -m pytest tests/test_grpc_services.py -v
```

### Smart Contracts (Hardhat)

```bash
cd contracts
npx hardhat test                          # all tests
npx hardhat test test/core/ --grep "payout"   # filter
REPORT_GAS=true npx hardhat test          # with gas report
npx hardhat coverage                       # Solidity coverage
```

### Oracle Node (Rust)

```bash
cd oracle-node
cargo test                                # all tests
cargo test -- --nocapture                # with stdout
cargo test crypto                         # filter by module
```

### API Gateway

```bash
cd api/gateway
npm test                                  # Jest tests
curl http://localhost:3001/health         # manual health check
```

---

## gRPC Development

### Regenerate Stubs After Proto Changes

```bash
# Install tools (once)
pip install grpcio-tools

# Regenerate
bash scripts/generate_grpc.sh
```

### Start gRPC Server

```bash
cd backend
python manage.py run_grpc_server
# → Starting gRPC server on [::]:50051
```

### Test with grpcurl

```bash
# List services
grpcurl -plaintext localhost:50051 list

# List methods of UssdService
grpcurl -plaintext localhost:50051 describe bimagrid.UssdService

# Call GetPolicyStatus
grpcurl -plaintext \
  -d '{"phone": "254700000000"}' \
  localhost:50051 bimagrid.UssdService/GetPolicyStatus

# Submit Oracle Data
grpcurl -plaintext \
  -d '{
    "oracle_id": "oracle-1",
    "h3_index": "8928308280fffff",
    "timestamp": "2026-07-02T23:00:00Z",
    "rainfall_mm": 12.5,
    "ndvi": 0.55,
    "soil_moisture": 0.28,
    "data_sources": ["nasa-power", "chirps"],
    "signature": "0xdeadbeef"
  }' \
  localhost:50051 bimagrid.OracleService/SubmitData
```

---

## Useful Commands

| Task | Command |
|---|---|
| Start all Docker services | `docker compose up -d` |
| Stop all services | `docker compose down` |
| Rebuild and restart | `docker compose up -d --build` |
| View backend logs | `docker compose logs -f backend` |
| Django shell | `docker compose exec backend python manage.py shell` |
| Run migrations | `docker compose exec backend python manage.py migrate` |
| Create superuser | `docker compose exec backend python manage.py createsuperuser` |
| Import crop risk data | `docker compose exec backend python manage.py import_crop_risk_constants` |
| Deploy contracts (local) | `cd contracts && npx hardhat run scripts/deploy.ts --network localhost` |
| Full backend test suite | `cd backend && pytest -v` |
| Full contract tests | `cd contracts && npx hardhat test` |
| Generate gRPC stubs | `bash scripts/generate_grpc.sh` |
| Run gRPC server | `cd backend && python manage.py run_grpc_server` |
| Celery worker (manual) | `cd backend && celery -A config worker -l INFO` |
| Check Celery tasks | `cd backend && celery -A config inspect active` |
| Oracle node (dev) | `cd oracle-node && cargo run` |
| Reset Docker volumes | `docker compose down -v` |

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `django.db.OperationalError: FATAL: role "bimagrid" does not exist` | Postgres not initialized | Run `docker compose up -d postgres` first and wait for healthcheck |
| `ModuleNotFoundError: No module named 'bimagrid_pb2'` | gRPC stubs not generated | Run `bash scripts/generate_grpc.sh` |
| `cargo: command not found` | Rust not installed | Run `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh` |
| `protoc: command not found` | protobuf-compiler missing | Ubuntu: `sudo apt install protobuf-compiler` / macOS: `brew install protobuf` |
| `EADDRINUSE :3001` | API Gateway port in use | `lsof -ti:3001 \| xargs kill` |
| Oracle `UnauthorizedOracle` revert | Oracle address not whitelisted | Call `oracle.setAuthorizedOracle(address, true)` from contract owner |
| `grpcurl: connection refused :50051` | gRPC server not running | `cd backend && python manage.py run_grpc_server` |
| M-Pesa callback not received | ngrok / tunnel needed | Use `ngrok http 8000` and set `MPESA_CALLBACK_BASE_URL=https://xxx.ngrok.io` |
| `celery: No module named config` | Wrong working directory | Always run Celery from `backend/` directory |
| Docker OOM (Out of Memory) | Insufficient RAM for all services | Increase Docker Desktop memory limit to ≥4GB, or start only core services |

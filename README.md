================================================================================
                              BIMAGRID
        Decentralized Parametric Climate Insurance Protocol


TABLE OF CONTENTS
-----------------
1. Project Overview
2. Problem Statement
3. Architecture Overview
4. Technical Stack
5. Installation & Setup
6. System Components
7. API Documentation
8. Smart Contract Specification
9. Oracle Node Architecture
10. Data Pipeline
11. Deployment Guide
12. Demo Instructions
13. Testing
14. Contributing
15. License & Credits

================================================================================
1. PROJECT OVERVIEW


BimaGrid is a standalone, decentralized, multi-peril parametric insurance 
protocol engineered specifically for smallholder and subsistence farmers in 
East Africa. By combining flexible high-resolution spatial indexing (Uber H3), 
cloud-native satellite computing (openEO), independent Rust Oracle Nodes, and 
trustless Smart Contract execution, BimaGrid completely removes human bias, 
manual claims adjustment, and multi-month delays from climate insurance.

KEY FEATURES:
- Zero-touch parametric payouts via M-Pesa within 60 seconds
- Multi-peril coverage (drought, flood, hail, frost, heat, pests)
- Flexible spatial resolution via Uber H3 hierarchical indexing
- Satellite-verified mitigation discounts via openEO
- Cryptographically auditable ledger for regulatory compliance
- Offline-first USSD interface for farmer accessibility
- Decentralized Oracle network preventing single points of failure

MISSION:
Turn satellite data into instant liquidity for the farmer who needs it most—
without a single human in the loop.

================================================================================
2. PROBLEM STATEMENT


Traditional agricultural insurance fails smallholder farmers due to:

A. BASIS RISK
   - Coarse 5km grids don't match 1-acre farm realities
   - Localized disasters (hail, flash floods) go uncompensated
   - Trust erosion from repeated "index said no, but my farm died" scenarios

B. ADMINISTRATIVE OVERHEAD
   - Physical claims adjustment costs exceed policy value
   - 60-90 day payout delays destroy farmer liquidity
   - Paper-heavy processes exclude unbanked populations

C. FRAUD & ADVERSE SELECTION
   - High-risk farmers self-select into voluntary programs
   - Mitigation discounts (drip irrigation) unverifiable at scale
   - Centralized databases vulnerable to manipulation

D. DATA VULNERABILITY
   - Single API feeds create single points of failure
   - No cryptographic proof of data integrity
   - Regulators cannot independently verify payouts

================================================================================
3. ARCHITECTURE OVERVIEW


BimaGrid operates on a three-plane architecture:

┌─────────────────────────────────────────────────────────────────────────┐
│                    FARMER / AGENT INTERFACE                              │
│         (USSD *384*XXX# | Agent Web Portal | SMS Alerts)                │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              PLANE 1: OPERATIONAL DATA PLANE                             │
│              (Django + PostGIS + openEO)                                 │
│                                                                          │
│  • Identity verification (IPRS integration)                             │
│  • Land registry queries (ArdhiSasa OCR)                                │
│  • H3 spatial indexing (Resolution 9 = ~0.1km²)                         │
│  • Satellite analytics via openEO (Sentinel-2, CHIRPS)                  │
│  • Premium calculation engine                                           │
│  • Policy manifest generation                                           │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              PLANE 2: CONSENSUS & ORACLE PLANE                           │
│              (Rust Network - 3 Independent Nodes)                        │
│                                                                          │
│  • Async data ingestion (CHIRPS, NASA POWER, Sentinel)                  │
│  • Multi-source data blending                                           │
│  • ECDSA cryptographic signing (Secp256k1)                              │
│  • Consensus calculation (median of 3 oracles)                          │
│  • JSON-RPC broadcast to blockchain                                     │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              PLANE 3: EXECUTION PLANE                                    │
│              (Smart Contract + Escrow)                                   │
│                                                                          │
│  • Signature verification (ecrecover)                                   │
│  • Consensus threshold evaluation                                       │
│  • Automated payout authorization                                       │
│  • M-Pesa B2C bridge trigger                                            │
│  • Immutable audit trail                                                │
└─────────────────────────────────────────────────────────────────────────┘

================================================================================
4. TECHNICAL STACK


BACKEND SERVICES:
- Django 4.2 (Python 3.10+) - Operational Data Plane
- PostgreSQL 15 + PostGIS 3.3 - Geospatial database
- Redis 7.0 - Caching and session management
- Celery 5.3 - Async task queue

ORACLE NODES:
- Rust 1.70+ with Tokio async runtime
- ethers-rs 2.0 - Blockchain interaction
- reqwest 0.11 - HTTP client
- sha2, k256 - Cryptographic operations
- serde, serde_json - Serialization

SMART CONTRACTS:
- Solidity 0.8.20
- Hardhat 2.17 - Development framework
- OpenZeppelin 4.9 - Security libraries

SATELLITE PROCESSING:
- openEO Python Client 1.0
- Google Earth Engine / Sentinel Hub backends
- H3-Py 3.7 - Uber's hexagonal spatial index

FRONTEND:
- React 18 (Agent Web Portal)
- TailwindCSS 3.3
- Africa's Talking USSD/SMS APIs
- M-Pesa Daraja API (B2C payments)

INFRASTRUCTURE:
- Docker & Docker Compose
- Nginx (reverse proxy)
- Let's Encrypt (SSL)
- AWS S3 (document storage)
- Cloudflare (CDN)

================================================================================
5. INSTALLATION & SETUP

PREREQUISITES:
- Docker 24.0+
- Docker Compose 2.20+
- Python 3.10+
- Rust 1.70+
- Node.js 18+
- PostgreSQL 15 client tools

STEP 1: CLONE REPOSITORY
$ git clone https://github.com/your-org/bimagrid.git
$ cd bimagrid

STEP 2: ENVIRONMENT CONFIGURATION
$ cp .env.example .env

Edit .env with your credentials:
- DATABASE_URL=postgresql://user:pass@localhost:5432/bimagrid
- REDIS_URL=redis://localhost:6379/0
- AFRICASTALKING_API_KEY=your_key
- AFRICASTALKING_USERNAME=your_username
- MPESA_CONSUMER_KEY=your_key
- MPESA_CONSUMER_SECRET=your_secret
- OPENEO_BACKEND_URL=https://earthengine.openeo.org
- OPENEO_USERNAME=your_username
- OPENEO_PASSWORD=your_password
- BLOCKCHAIN_RPC_URL=http://localhost:8545
- ORACLE_PRIVATE_KEY=0x... (64-char hex)

STEP 3: BUILD AND START SERVICES
$ docker-compose up -d --build

This starts:
- Django web server (port 8000)
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- Celery worker
- Nginx reverse proxy (port 80)

STEP 4: DATABASE MIGRATIONS
$ docker-compose exec web python manage.py migrate
$ docker-compose exec web python manage.py collectstatic --noinput

STEP 5: CREATE ADMIN USER
$ docker-compose exec web python manage.py createsuperuser

STEP 6: INITIALIZE SPATIAL DATA
$ docker-compose exec web python manage.py load_h3_grids --resolution=9
$ docker-compose exec web python manage.py import_crop_risk_constants
$ docker-compose exec web python manage.py import_historical_weather_data

STEP 7: BUILD ORACLE NODES
$ cd oracle-node
$ cargo build --release
$ cd ..

STEP 8: DEPLOY SMART CONTRACTS
$ cd contracts
$ npm install
$ npx hardhat compile
$ npx hardhat run scripts/deploy.js --network localhost
$ cd ..

STEP 9: START ORACLE NODES (3 instances)
$ ./oracle-node/target/release/bimagrid-oracle --config oracle-config-1.toml &
$ ./oracle-node/target/release/bimagrid-oracle --config oracle-config-2.toml &
$ ./oracle-node/target/release/bimagrid-oracle --config oracle-config-3.toml &

STEP 10: VERIFY SYSTEM
$ curl http://localhost/api/health
Expected: {"status": "healthy", "version": "1.0.0"}

================================================================================
6. SYSTEM COMPONENTS


6.1 DJANGO OPERATIONAL DATA PLANE
---------------------------------
Location: /bimagrid-web/

Key Modules:
- apps/onboarding/ - 5-tier farmer verification
- apps/policies/ - Policy lifecycle management
- apps/pricing/ - Actuarial premium calculation
- apps/oracles/ - Oracle data aggregation
- apps/payments/ - M-Pesa integration
- apps/verification/ - openEO satellite analytics

Database Models:
- Farmer (identity, contact, verification status)
- LandParcel (geometry, H3_index, ownership_docs)
- Policy (crop, acreage, premium, coverage_window)
- OracleSubmission (data_hash, signature, timestamp)
- Payout (policy, amount, tx_hash, status)

6.2 RUST ORACLE NODE
--------------------
Location: /oracle-node/

Architecture:
- Scheduler: Tokio interval timer (23:00 EAT daily)
- Data Ingestion: reqwest HTTP client
- Cryptographic Signer: k256 ECDSA (Secp256k1)
- Blockchain Broadcaster: ethers-rs JSON-RPC

Configuration (oracle-config-1.toml):
[node]
id = "oracle-1"
data_sources = ["open-meteo", "nasa-power"]
signing_key = "0x..."

[blockchain]
rpc_url = "http://localhost:8545"
contract_address = "0x..."
gas_limit = 500000

[schedule]
evaluation_time = "23:00"
timezone = "Africa/Nairobi"

6.3 SMART CONTRACTS
-------------------
Location: /contracts/

Contracts:
- KilimaShieldOracle.sol - Oracle data receiver & consensus
- PolicyRegistry.sol - Policy minting & management
- EscrowVault.sol - Premium pooling & payout execution
- MitigationVerifier.sol - Discount validation

Deployment Addresses (localhost):
- Oracle: 0x5FbDB2315678afecb367f032d93F642f64180aa3
- PolicyRegistry: 0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
- EscrowVault: 0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0

================================================================================
7. API DOCUMENTATION


BASE URL: http://localhost/api/v1/

AUTHENTICATION:
- USSD endpoints: No auth (Africa's Talking webhook)
- Admin endpoints: Session-based auth
- Agent endpoints: JWT token

USSD GATEWAY
POST /ussd/gateway/
Request:
  sessionId=ATUid_123&phoneNumber=254712345678&text=

Response (Screen 1):
  CON Welcome to BimaGrid.
  1. Register Farm
  2. Check Policy Status
  3. File Claim

Request (User selects 1):
  sessionId=ATUid_123&phoneNumber=254712345678&text=1

Response (Screen 2):
  CON Enter your 4-digit Ward Code:

[... continues through registration flow ...]

POLICY MANAGEMENT
GET /policies/{policy_id}/
Headers: Authorization: Bearer {token}
Response:
{
  "id": "POL-98765",
  "farmer_phone": "254712345678",
  "h3_index": "8928308280fffff",
  "crop_type": "maize",
  "acreage": 2.5,
  "premium_kes": 450.00,
  "coverage_start": "2026-03-01",
  "coverage_end": "2026-09-30",
  "status": "ACTIVE",
  "mitigation_discounts": ["drip_irrigation"],
  "on_chain_tx": "0xabc123..."
}

ORACLE DATA SUBMISSION (Internal API)
POST /oracles/submit-data/
Headers: X-Oracle-Signature: {ecdsa_sig}
Body:
{
  "oracle_id": "oracle-1",
  "h3_index": "8928308280fffff",
  "timestamp": "2026-07-01T23:00:00Z",
  "rainfall_mm": 45.2,
  "ndvi": 0.65,
  "soil_moisture": 0.38,
  "data_sources": ["open-meteo", "sentinel-2"]
}

PAYOUT TRIGGER (Webhook from Smart Contract)
POST /payments/payout-trigger/
Body:
{
  "policy_id": "POL-98765",
  "amount_kes": 5000.00,
  "tx_hash": "0xdef456...",
  "event": "PayoutAuthorized"
}

================================================================================
8. SMART CONTRACT SPECIFICATION


CONTRACT: KilimaShieldOracle
ADDRESS: 0x5FbDB2315678afecb367f032d93F642f64180aa3

KEY FUNCTIONS:

function submitData(
    bytes32 h3Index,
    uint256 timestamp,
    uint256 rainfall,
    uint256 ndvi,
    bytes memory signature
) external

  - Verifies ECDSA signature against authorized oracle addresses
  - Stores submission in oracleSubmissions[h3Index][timestamp]
  - When 3 submissions received, calculates median
  - If median triggers threshold, calls evaluatePolicies()

function evaluatePolicies(bytes32 h3Index, uint256 timestamp) internal

  - Iterates through active policies in h3Index
  - Checks if median rainfall < policy threshold
  - If true, sets policy.paidOut = true
  - Transfers payoutAmount from escrow to farmer address
  - Emits PayoutTriggered event

function registerPolicy(
    uint256 policyId,
    address farmer,
    bytes32 h3Index,
    uint256 threshold,
    uint256 payoutAmount
) external onlyAdmin

  - Creates policy record
  - Requires premium payment to escrow

EVENTS:

event PolicyRegistered(uint256 indexed policyId, address farmer, bytes32 h3Index)
event DataSubmitted(address indexed oracle, bytes32 h3Index, uint256 timestamp)
event ConsensusReached(bytes32 h3Index, uint256 timestamp, uint256 medianValue)
event PayoutTriggered(uint256 indexed policyId, address farmer, uint256 amount)

GAS OPTIMIZATION:
- Uses storage packing for policy structs
- Median calculation uses sorting network (no loops)
- Batch payout processing for multiple policies in same hexagon

================================================================================
9. ORACLE NODE ARCHITECTURE


NODE EXECUTION FLOW:

1. SCHEDULER WAKEUP (23:00 EAT daily)
   └─> Tokio interval timer triggers evaluation cycle

2. DATA INGESTION (Parallel async tasks)
   ├─> Fetch CHIRPS-RT rainfall data for target H3 hexagons
   ├─> Fetch NASA POWER temperature data
   ├─> Fetch Sentinel-2 NDVI via openEO batch job
   └─> Normalize all values to integers (mm * 100, NDVI * 10000)

3. PAYLOAD CONSTRUCTION
   └─> Build struct: {h3_index, timestamp, rainfall, ndvi, soil_moisture}

4. CRYPTOGRAPHIC SIGNING
   ├─> Serialize payload to bytes (abi.encodePacked equivalent)
   ├─> Hash with Keccak-256
   └─> Sign hash with ECDSA private key (Secp256k1)

5. BLOCKCHAIN BROADCAST
   ├─> Construct transaction calling submitData()
   ├─> Estimate gas (typically 150,000-200,000)
   ├─> Sign transaction with oracle wallet
   └─> Broadcast via JSON-RPC (eth_sendRawTransaction)

6. RECEIPT CONFIRMATION
   └─> Wait for transaction receipt (12-15 seconds on PoA chain)

CODE EXAMPLE (Rust):

use ethers::prelude::*;
use ethers::utils::keccak256;

async fn submit_oracle_data(
    provider: &Provider<Http>,
    wallet: LocalWallet,
    contract_address: Address,
    h3_index: [u8; 32],
    timestamp: u64,
    rainfall: u64,
    ndvi: u64
) -> Result<(), Box<dyn std::error::Error>> {
    
    // 1. Construct payload
    let payload = ethers::abi::encode_packed(&[
        Token::FixedBytes(h3_index.to_vec()),
        Token::Uint(timestamp.into()),
        Token::Uint(rainfall.into()),
        Token::Uint(ndvi.into()),
    ])?;
    
    // 2. Hash and sign
    let hash = keccak256(&payload);
    let signature = wallet.sign_hash(H256::from(hash))?;
    
    // 3. Encode function call
    let calldata = /* ... ABI encode submitData(h3, ts, rain, ndvi, sig) ... */;
    
    // 4. Broadcast transaction
    let tx = TransactionRequest::new()
        .to(contract_address)
        .data(calldata)
        .from(wallet.address());
    
    let pending_tx = provider.send_transaction(tx, None).await?;
    let receipt = pending_tx.await?;
    
    println!("Oracle data submitted. Tx: {:?}", receipt.unwrap().transaction_hash);
    Ok(())
}

================================================================================
10. DATA PIPELINE


10.1 SATELLITE DATA VIA openEO
-------------------------------
Purpose: Verify mitigation measures and calculate crop health indices

Example: Verify Drip Irrigation via NDWI (Normalized Difference Water Index)

import openeo

con = openeo.connect("https://earthengine.openeo.org")
con.authenticate_basic("username", "password")

# Load Sentinel-2 data for farm polygon
datacube = con.load_collection(
    "SENTINEL2_L2A",
    spatial_extent={"west": 36.80, "south": -1.30, "east": 36.81, "north": -1.29},
    temporal_extent=["2026-06-01", "2026-06-15"],
    bands=["B03", "B08"]  # Green, NIR
)

# Calculate NDWI
green = datacube.band("B03")
nir = datacube.band("B08")
ndwi = (green - nir) / (green + nir)

# Aggregate to farm-level mean
farm_mean_ndwi = ndwi.aggregate_spatial(
    geometries=farm_polygon_geojson,
    reducer="mean"
)

# Execute batch job
job = farm_mean_ndwi.create_job()
job.start_and_wait()
results = job.get_results().download_files("output")
# Result: {"mean": 0.45} -> VERIFIED IRRIGATION

10.2 WEATHER DATA BLENDING
---------------------------
Purpose: Reduce basis risk by combining coarse CHIRPS with high-res satellite

Algorithm:
1. Fetch CHIRPS 5km pixel for region
2. Fetch Sentinel-2 soil moisture for farm H3 hexagon
3. Apply Inverse Distance Weighting interpolation
4. Generate farm-specific rainfall estimate
5. Submit blended value to Oracle

10.3 HISTORICAL RISK CALCULATION
---------------------------------
Purpose: Calculate R_peril for actuarial pricing

Data Sources:
- CHIRPS final (2000-2025) for rainfall history
- ERA5 reanalysis for temperature history
- SRTM DEM for topographic weighting

Process:
1. For each H3 Resolution 9 hexagon:
   - Calculate 20-year mean rainfall
   - Calculate 95th percentile daily rainfall (flood threshold)
   - Calculate frost days (temp < 2°C)
   - Calculate heat stress days (temp > 35°C during flowering)
2. Store in grid_risk PostGIS table
3. Query during premium calculation

================================================================================
11. DEPLOYMENT GUIDE


PRODUCTION DEPLOYMENT (AWS Example):

INFRASTRUCTURE:
- EC2 t3.large (Django + Celery)
- RDS PostgreSQL (db.r5.large, Multi-AZ)
- ElastiCache Redis (cache.r6g.large)
- S3 bucket (document storage)
- CloudFront (static assets)
- Route53 (DNS)
- ACM (SSL certificates)

DEPLOYMENT STEPS:

1. Provision infrastructure via Terraform
   $ cd infra/terraform
   $ terraform init
   $ terraform apply

2. Configure environment variables in AWS Secrets Manager

3. Build Docker images and push to ECR
   $ docker build -t bimagrid-web -f Dockerfile.web .
   $ docker tag bimagrid-web:latest {account}.dkr.ecr.{region}.amazonaws.com/bimagrid-web:latest
   $ docker push {account}.dkr.ecr.{region}.amazonaws.com/bimagrid-web:latest

4. Deploy to ECS Fargate
   $ aws ecs update-service --cluster bimagrid --service web --force-new-deployment

5. Deploy Oracle Nodes to EC2 instances
   $ ansible-playbook -i inventory/production deploy-oracles.yml

6. Deploy Smart Contracts to production blockchain
   $ cd contracts
   $ npx hardhat run scripts/deploy.js --network mainnet

7. Configure DNS and SSL
   $ aws route53 change-resource-record-sets --hosted-zone-id {zone} --change-batch file:changes.json

MONITORING:
- CloudWatch Logs (application logs)
- CloudWatch Metrics (CPU, memory, request count)
- X-Ray (distributed tracing)
- PagerDuty (alerting)

SCALING:
- Django: Auto-scaling group (2-10 instances based on CPU)
- Celery: Auto-scaling group (2-20 workers based on queue depth)
- Oracle Nodes: Fixed 3 instances (consensus requirement)
- Database: Read replicas for query scaling

================================================================================
12. DEMO INSTRUCTIONS


HACKATHON DEMO SETUP:

PREREQUISITES:
- All services running locally (docker-compose up)
- Africa's Talking sandbox credentials configured
- M-Pesa Daraja sandbox credentials configured
- Test phone numbers registered in sandbox

DEMO SCRIPT (5 minutes):

MINUTE 0:00-1:00 - INTRODUCTION
- Show architecture diagram
- Explain 3-plane design
- Highlight key innovations (H3, openEO, Rust Oracles)

MINUTE 1:00-2:00 - FARMER ONBOARDING
- Open Africa's Talking USSD simulator
- Dial *384*XXX#
- Walk through registration:
  * Enter ward code
  * Select crop (Maize)
  * Enter acreage (2.5)
  * Confirm M-Pesa number
- Show "Registration Complete" END screen
- Open Django admin, show new policy record
- Show blockchain transaction (policy minted on-chain)

MINUTE 2:00-3:00 - ORACLE CONSENSUS
- Open terminal showing 3 Oracle node logs
- Trigger manual evaluation (God Mode):
  $ curl -X POST http://localhost:8000/api/admin/trigger-evaluation/ \
    -H "Authorization: Bearer {admin_token}" \
    -d '{"h3_index": "8928308280fffff", "simulate_drought": true}'
- Show Oracle logs:
  * Oracle-1: Fetching CHIRPS data... rainfall=15mm
  * Oracle-2: Fetching NASA data... rainfall=18mm
  * Oracle-3: Fetching Sentinel data... rainfall=12mm
  * Consensus: Median=15mm (below 30mm threshold)
  * Signing payload... Broadcasting to blockchain...
- Show blockchain transaction (data submitted)

MINUTE 3:00-4:00 - AUTOMATED PAYOUT
- Show smart contract execution:
  * ConsensusReached event emitted
  * evaluatePolicies() called
  * PayoutTriggered event emitted
- Hold up phone
- Receive M-Pesa SMS:
  "BimaGrid Alert: Drought detected in your area. KES 5,000 sent to your 
   M-Pesa account. Tx: 0xabc123... Hash: 0xdef456..."
- Show Django admin: Policy status = PAID_OUT

MINUTE 4:00-5:00 - REGULATORY AUDIT
- Open block explorer (or custom audit UI)
- Show complete transaction history:
  * Policy registration
  * Oracle data submissions (3 signatures)
  * Consensus calculation
  * Payout execution
- Emphasize: "Every step cryptographically verifiable by IRA"
- Final slide: Value proposition summary

GOD MODE ENDPOINTS:

# Simulate drought for specific H3 hexagon
POST /api/admin/simulate-drought/
{
  "h3_index": "8928308280fffff",
  "rainfall_mm": 15.0,
  "ndvi": 0.35
}

# Force immediate Oracle evaluation
POST /api/admin/trigger-evaluation/
{
  "h3_index": "8928308280fffff"
}

# Bypass M-Pesa STK push (auto-activate policy)
POST /api/admin/bypass-payment/
{
  "policy_id": "POL-98765"
}

================================================================================
13. TESTING


UNIT TESTS:

Django:
$ docker-compose exec web python manage.py test apps/

Coverage:
$ docker-compose exec web coverage run --source='apps' manage.py test
$ docker-compose exec web coverage report

Rust Oracle:
$ cd oracle-node
$ cargo test

Smart Contracts:
$ cd contracts
$ npx hardhat test

INTEGRATION TESTS:

End-to-end policy lifecycle:
$ pytest tests/integration/test_policy_lifecycle.py

Oracle consensus:
$ pytest tests/integration/test_oracle_consensus.py

M-Pesa payout:
$ pytest tests/integration/test_mpesa_payout.py

LOAD TESTING:

Simulate 10,000 concurrent USSD sessions:
$ locust -f tests/load/ussd_load_test.py --host=http://localhost

Simulate Oracle node throughput:
$ cd oracle-node
$ cargo bench

================================================================================
14. CONTRIBUTING

DEVELOPMENT WORKFLOW:

1. Fork the repository
2. Create feature branch (git checkout -b feature/amazing-feature)
3. Commit changes (git commit -m 'Add amazing feature')
4. Push to branch (git push origin feature/amazing-feature)
5. Open Pull Request

CODE STANDARDS:

Python:
- Follow PEP 8
- Use black for formatting
- Use isort for import sorting
- Type hints required for all functions

Rust:
- Follow rustfmt conventions
- Use clippy for linting
- Document all public functions

Solidity:
- Follow Solidity style guide
- Use Slither for static analysis
- Gas optimization required

COMMIT MESSAGES:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Formatting, no code logic change
- refactor: Code change that neither fixes a bug nor adds a feature
- test: Adding missing tests
- chore: Changes to build process or auxiliary tools

================================================================================
15. LICENSE & CREDITS


LICENSE:
Apache License 2.0

CREDITS:

Core Team:
- [Your Name] - Architecture & Smart Contracts
- [Team Member 1] - Django Backend & openEO Integration
- [Team Member 2] - Rust Oracle Nodes
- [Team Member 3] - Frontend & USSD Integration

Acknowledgments:
- Africa's Talking - USSD/SMS API infrastructure
- openEO Consortium - Satellite processing framework
- Uber Engineering - H3 spatial indexing library
- Ethereum Foundation - Smart contract platform
- Parity Technologies - Rust blockchain libraries

Data Sources:
- CHIRPS (UC Santa Barbara) - Precipitation data
- NASA POWER - Meteorological data
- Sentinel Hub - Satellite imagery
- Google Earth Engine - Geospatial processing

Partners:
- Insurance Regulatory Authority (IRA) Kenya
- African Risk Capacity (ARC)
- Swiss Re Institute

================================================================================
                              END OF README


For questions, contact: [stanlleylocke@gmail.com]
Documentation: https://docs.bimagrid.io
Discord: https://discord.gg/bimagrid
Twitter: @BimaGridProtocol

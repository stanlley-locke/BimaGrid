# BimaGrid Workflow & Project Structure

## Document Metadata

| Field | Value |
| --- | --- |
| Document Version | 1.0.0 |
| Last Updated | July 1, 2026 |
| Maintainer | BimaGrid Engineering Team |

## Table of Contents

1. Project Structure Overview
2. Root Directory Layout
3. Backend Structure (Django)
4. Frontend Structure (React)
5. API Layer Structure
6. USSD Layer Structure
7. Oracle Node Structure (Rust)
8. Smart Contract Structure
9. Infrastructure Structure
10. Documentation Structure
11. Development Pipeline
12. Git Workflow
13. CI/CD Pipeline
14. Local Development Workflow
15. Deployment Workflow
16. Environment Management
17. Dependency Management
18. Code Review Process
19. Release Process
20. Incident Response Workflow

## 1. Project Structure Overview

BimaGrid follows a monorepo structure with clear separation of concerns:

```text
bimagrid/
├── backend/              # Django Operational Data Plane
├── frontend/             # React Agent Web Portal
├── oracle-node/          # Rust Oracle Nodes
├── contracts/            # Solidity Smart Contracts
├── ussd/                 # USSD Gateway Service
├── api/                  # API Gateway & Documentation
├── infrastructure/       # Terraform, Docker, CI/CD
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── tests/                # Integration & E2E tests
└── README.md             # Project overview
```

Each component is independently deployable but shares common configurations and utilities through the /shared directory.

## 2. Root Directory Layout

```text
bimagrid/
│
├── .github/                      # GitHub-specific configurations
│   ├── workflows/                # CI/CD workflows
│   │   ├── ci.yml               # Continuous integration
│   │   ├── deploy-staging.yml   # Staging deployment
│   │   ├── deploy-production.yml # Production deployment
│   │   └── security-scan.yml    # Security scanning
│   ├── ISSUE_TEMPLATE/          # Issue templates
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── security_vulnerability.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CODEOWNERS               # Code ownership rules
│
├── .husky/                       # Git hooks
│   ├── pre-commit               # Pre-commit hook
│   └── commit-msg               # Commit message validation
│
├── backend/                      # Django backend (see Section 3)
├── frontend/                     # React frontend (see Section 4)
├── oracle-node/                  # Rust oracle nodes (see Section 7)
├── contracts/                    # Solidity contracts (see Section 8)
├── ussd/                         # USSD gateway (see Section 6)
├── api/                          # API layer (see Section 5)
│
├── infrastructure/               # Infrastructure as Code
│   ├── terraform/               # Terraform configurations
│   │   ├── environments/        # Environment-specific configs
│   │   │   ├── dev/
│   │   │   ├── staging/
│   │   │   └── production/
│   │   ├── modules/             # Reusable Terraform modules
│   │   │   ├── vpc/
│   │   │   ├── ecs/
│   │   │   ├── rds/
│   │   │   └── s3/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── docker/                  # Docker configurations
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.dev.yml
│   │   ├── docker-compose.prod.yml
│   │   └── Dockerfiles/
│   │       ├── backend.dockerfile
│   │       ├── frontend.dockerfile
│   │       ├── oracle.dockerfile
│   │       └── ussd.dockerfile
│   ├── ansible/                 # Ansible playbooks
│   │   ├── playbooks/
│   │   ├── inventory/
│   │   └── roles/
│   └── kubernetes/              # Kubernetes manifests
│       ├── base/
│       ├── overlays/
│       └── helm/
│
├── docs/                         # Documentation (see Section 10)
├── scripts/                      # Utility scripts
│   ├── setup.sh                 # Initial setup script
│   ├── seed_db.py               # Database seeding
│   ├── deploy.sh                # Deployment script
│   ├── backup.sh                # Backup script
│   └── migrate.sh               # Migration script
│
├── tests/                        # Cross-component tests
│   ├── integration/             # Integration tests
│   ├── e2e/                     # End-to-end tests
│   ├── load/                    # Load tests
│   └── fixtures/                # Test data
│
├── shared/                       # Shared utilities
│   ├── types/                   # Shared type definitions
│   ├── constants/               # Shared constants
│   ├── utils/                   # Shared utilities
│   └── config/                  # Shared configurations
│
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── .dockerignore                 # Docker ignore rules
├── .pre-commit-config.yaml       # Pre-commit hooks config
├── Makefile                      # Common commands
├── LICENSE                       # Apache 2.0 license
└── README.md                     # Project README
```

## 3. Backend Structure (Django)

```text
backend/
│
├── config/                       # Django project configuration
│   ├── __init__.py
│   ├── settings/                # Settings modules
│   │   ├── __init__.py
│   │   ├── base.py             # Base settings
│   │   ├── development.py      # Development overrides
│   │   ├── staging.py          # Staging overrides
│   │   ├── production.py       # Production overrides
│   │   └── testing.py          # Testing overrides
│   ├── urls.py                  # Root URL configuration
│   ├── wsgi.py                  # WSGI application
│   ├── asgi.py                  # ASGI application
│   └── celery.py                # Celery configuration
│
├── apps/                         # Django applications
│   │
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── models.py            # Base models, mixins
│   │   ├── middleware.py        # Custom middleware
│   │   ├── exceptions.py        # Custom exceptions
│   │   ├── validators.py        # Custom validators
│   │   ├── utils.py             # Utility functions
│   │   ├── constants.py         # Project constants
│   │   └── admin.py             # Admin customizations
│   │
│   ├── accounts/                 # User management
│   │   ├── __init__.py
│   │   ├── models.py            # User, Profile models
│   │   ├── serializers.py       # DRF serializers
│   │   ├── views.py             # API views
│   │   ├── urls.py              # URL routing
│   │   ├── admin.py             # Admin interface
│   │   ├── permissions.py       # Custom permissions
│   │   ├── authentication.py    # Custom auth backends
│   │   ├── signals.py           # Django signals
│   │   ├── tasks.py             # Celery tasks
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   ├── test_views.py
│   │   │   └── test_serializers.py
│   │   └── migrations/
│   │
│   ├── onboarding/               # Farmer onboarding (5-tier)
│   │   ├── __init__.py
│   │   ├── models.py            # Farmer, LandParcel models
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── services.py          # Business logic
│   │   ├── validators.py        # Document validation
│   │   ├── tasks.py             # Async verification tasks
│   │   ├── signals.py
│   │   ├── constants.py
│   │   ├── tests/
│   │   └── migrations/
│   │
│   ├── policies/                 # Policy management
│   │   ├── __init__.py
│   │   ├── models.py            # Policy, Coverage models
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── services.py
│   │   ├── tasks.py
│   │   ├── signals.py
│   │   ├── constants.py
│   │   ├── tests/
│   │   └── migrations/
│   │
│   ├── pricing/                  # Actuarial pricing engine
│   │   ├── __init__.py
│   │   ├── models.py            # Risk factors, pricing rules
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── engine.py            # Pricing calculation logic
│   │   ├── formulas.py          # Actuarial formulas
│   │   ├── risk_matrices.py     # Risk lookup tables
│   │   ├── tasks.py
│   │   ├── tests/
│   │   └── migrations/
│   │
│   ├── oracles/                  # Oracle data management
│   │   ├── __init__.py
│   │   ├── models.py            # OracleSubmission, Consensus
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── services.py          # Oracle data processing
│   │   ├── aggregators.py       # Multi-source data blending
│   │   ├── tasks.py
│   │   ├── tests/
│   │   └── migrations/
│   │
│   ├── verification/             # Mitigation verification
│   │   ├── __init__.py
│   │   ├── models.py            # Mitigation, Verification
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── services.py
│   │   ├── satellite.py         # openEO integration
│   │   ├── image_analysis.py    # Computer vision
│   │   ├── tasks.py
│   │   ├── tests/
│   │   └── migrations/
│   │
│   ├── payments/                 # M-Pesa integration
│   │   ├── __init__.py
│   │   ├── models.py            # Transaction, Payout
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── services.py          # Payment processing
│   │   ├── mpesa.py             # Daraja API client
│   │   ├── webhooks.py          # Callback handlers
│   │   ├── tasks.py
│   │   ├── tests/
│   │   └── migrations/
│   │
│   ├── claims/                   # Claims processing
│   │   ├── __init__.py
│   │   ├── models.py            # Claim, Dispute
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── services.py
│   │   ├── tasks.py
│   │   ├── tests/
│   │   └── migrations/
│   │
│   ├── notifications/            # SMS, email, push
│   │   ├── __init__.py
│   │   ├── models.py            # Notification, Template
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── services.py
│   │   ├── sms.py               # Africa's Talking SMS
│   │   ├── email.py             # Email service
│   │   ├── tasks.py
│   │   ├── tests/
│   │   └── migrations/
│   │
│   ├── geospatial/               # Spatial data management
│   │   ├── __init__.py
│   │   ├── models.py            # H3Grid, Region
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── services.py
│   │   ├── h3_utils.py          # H3 indexing utilities
│   │   ├── spatial_queries.py   # PostGIS queries
│   │   ├── tasks.py
│   │   ├── tests/
│   │   └── migrations/
│   │
│   ├── satellite/                # Satellite data processing
│   │   ├── __init__.py
│   │   ├── models.py            # SatelliteJob, Result
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── services.py
│   │   ├── openeo_client.py     # openEO API client
│   │   ├── process_graphs.py    # Process graph definitions
│   │   ├── tasks.py
│   │   ├── tests/
│   │   └── migrations/
│   │
│   └── admin_dashboard/          # Admin web interface
│       ├── __init__.py
│       ├── views.py
│       ├── urls.py
│       ├── templates/
│       └── static/
│
├── services/                     # Business logic services
│   ├── __init__.py
│   ├── policy_service.py
│   ├── pricing_service.py
│   ├── oracle_service.py
│   ├── payment_service.py
│   └── notification_service.py
│
├── integrations/                 # External API clients
│   ├── __init__.py
│   ├── africastalking.py        # Africa's Talking client
│   ├── mpesa.py                 # M-Pesa Daraja client
│   ├── iprs.py                  # IPRS identity client
│   ├── ardisasa.py              # ArdhiSasa land registry
│   ├── chirps.py                # CHIRPS weather data
│   ├── nasa_power.py            # NASA POWER client
│   ├── openeo.py                # openEO client
│   └── blockchain.py            # Blockchain RPC client
│
├── middleware/                   # Custom middleware
│   ├── __init__.py
│   ├── authentication.py
│   ├── logging.py
│   ├── rate_limiting.py
│   └── cors.py
│
├── management/                   # Custom management commands
│   └── commands/
│       ├── seed_h3_grids.py
│       ├── import_weather_data.py
│       ├── calculate_risk_scores.py
│       └── sync_blockchain.py
│
├── static/                       # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/                    # Django templates
│   ├── base.html
│   ├── admin/
│   └── emails/
│
├── locale/                       # Internationalization
│   ├── en/
│   └── sw/
│
├── tests/                        # Project-wide tests
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── factories.py             # Factory Boy factories
│   └── utils.py                 # Test utilities
│
├── fixtures/                     # Test data fixtures
│   ├── farmers.json
│   ├── policies.json
│   └── h3_grids.json
│
├── logs/                         # Application logs
│
├── requirements/                 # Python dependencies
│   ├── base.txt                 # Core dependencies
│   ├── development.txt          # Dev dependencies
│   ├── testing.txt              # Test dependencies
│   └── production.txt           # Production dependencies
│
├── manage.py                     # Django management script
├── pytest.ini                    # Pytest configuration
├── setup.cfg                     # Package configuration
├── pyproject.toml                # Project metadata
└── .flake8                       # Flake8 configuration
```

## 4. Frontend Structure (React)

```text
frontend/
│
├── public/                       # Static assets
│   ├── index.html
│   ├── favicon.ico
│   ├── manifest.json
│   └── robots.txt
│
├── src/                          # Source code
│   │
│   ├── assets/                   # Static assets
│   │   ├── images/
│   │   ├── icons/
│   │   ├── fonts/
│   │   └── styles/
│   │       ├── globals.css
│   │       ├── tailwind.css
│   │       └── variables.css
│   │
│   ├── components/               # Reusable components
│   │   ├── ui/                  # Base UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Alert.tsx
│   │   │   ├── Spinner.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── forms/               # Form components
│   │   │   ├── FormField.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Checkbox.tsx
│   │   │   ├── Radio.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   ├── DateInput.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── layout/              # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Container.tsx
│   │   │   └── index.ts
│   │   │
│   │   ├── maps/                # Map components
│   │   │   ├── Map.tsx
│   │   │   ├── MapMarker.tsx
│   │   │   ├── MapPolygon.tsx
│   │   │   ├── H3Grid.tsx
│   │   │   └── index.ts
│   │   │
│   │   └── charts/              # Chart components
│   │       ├── LineChart.tsx
│   │       ├── BarChart.tsx
│   │       ├── PieChart.tsx
│   │       └── index.ts
│   │
│   ├── features/                 # Feature-based modules
│   │   │
│   │   ├── auth/                # Authentication
│   │   │   ├── components/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── RegisterForm.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useAuth.ts
│   │   │   │   └── useLogin.ts
│   │   │   ├── services/
│   │   │   │   └── authService.ts
│   │   │   ├── store/
│   │   │   │   └── authStore.ts
│   │   │   ├── types/
│   │   │   │   └── auth.types.ts
│   │   │   └── index.ts
│   │   │
│   │   ├── farmers/             # Farmer management
│   │   │   ├── components/
│   │   │   │   ├── FarmerList.tsx
│   │   │   │   ├── FarmerDetail.tsx
│   │   │   │   ├── FarmerForm.tsx
│   │   │   │   └── FarmerTable.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useFarmers.ts
│   │   │   │   └── useFarmer.ts
│   │   │   ├── services/
│   │   │   │   └── farmerService.ts
│   │   │   ├── store/
│   │   │   │   └── farmerStore.ts
│   │   │   ├── types/
│   │   │   │   └── farmer.types.ts
│   │   │   └── index.ts
│   │   │
│   │   ├── policies/            # Policy management
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   ├── store/
│   │   │   ├── types/
│   │   │   └── index.ts
│   │   │
│   │   ├── onboarding/          # Onboarding workflow
│   │   │   ├── components/
│   │   │   │   ├── StepIndicator.tsx
│   │   │   │   ├── IdentityStep.tsx
│   │   │   │   ├── LandStep.tsx
│   │   │   │   ├── FarmStep.tsx
│   │   │   │   ├── PhotoStep.tsx
│   │   │   │   └── PaymentStep.tsx
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   ├── store/
│   │   │   ├── types/
│   │   │   └── index.ts
│   │   │
│   │   ├── verification/        # Mitigation verification
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   ├── store/
│   │   │   ├── types/
│   │   │   └── index.ts
│   │   │
│   │   ├── claims/              # Claims management
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   ├── store/
│   │   │   ├── types/
│   │   │   └── index.ts
│   │   │
│   │   └── dashboard/           # Admin dashboard
│   │       ├── components/
│   │       │   ├── StatsCard.tsx
│   │       │   ├── RecentActivity.tsx
│   │       │   ├── MapOverview.tsx
│   │       │   └── Charts.tsx
│   │       ├── hooks/
│   │       ├── services/
│   │       ├── store/
│   │       ├── types/
│   │       └── index.ts
│   │
│   ├── pages/                    # Page components
│   │   ├── Home.tsx
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Farmers.tsx
│   │   ├── FarmerDetail.tsx
│   │   ├── Policies.tsx
│   │   ├── PolicyDetail.tsx
│   │   ├── Onboarding.tsx
│   │   ├── Verification.tsx
│   │   ├── Claims.tsx
│   │   ├── Reports.tsx
│   │   ├── Settings.tsx
│   │   └── NotFound.tsx
│   │
│   ├── hooks/                    # Global custom hooks
│   │   ├── useApi.ts
│   │   ├── useDebounce.ts
│   │   ├── useLocalStorage.ts
│   │   ├── useMediaQuery.ts
│   │   ├── useClickOutside.ts
│   │   └── index.ts
│   │
│   ├── services/                 # API services
│   │   ├── api.ts               # Axios instance
│   │   ├── authService.ts
│   │   ├── farmerService.ts
│   │   ├── policyService.ts
│   │   ├── onboardingService.ts
│   │   ├── verificationService.ts
│   │   ├── claimsService.ts
│   │   └── index.ts
│   │
│   ├── store/                    # Global state management
│   │   ├── index.ts
│   │   ├── authStore.ts
│   │   ├── uiStore.ts
│   │   └── notificationStore.ts
│   │
│   ├── types/                    # Global TypeScript types
│   │   ├── api.types.ts
│   │   ├── farmer.types.ts
│   │   ├── policy.types.ts
│   │   ├── common.types.ts
│   │   └── index.ts
│   │
│   ├── utils/                    # Utility functions
│   │   ├── api.ts               # API helpers
│   │   ├── format.ts            # Data formatting
│   │   ├── validation.ts        # Validation helpers
│   │   ├── storage.ts           # Local storage helpers
│   │   ├── date.ts              # Date utilities
│   │   ├── geo.ts               # Geospatial utilities
│   │   ├── h3.ts                # H3 utilities
│   │   └── index.ts
│   │
│   ├── constants/                # Constants
│   │   ├── api.ts
│   │   ├── routes.ts
│   │   ├── crops.ts
│   │   ├── perils.ts
│   │   └── index.ts
│   │
│   ├── config/                   # Configuration
│   │   ├── env.ts               # Environment variables
│   │   ├── api.ts               # API configuration
│   │   └── map.ts               # Map configuration
│   │
│   ├── lib/                      # Third-party library wrappers
│   │   ├── mapbox.ts
│   │   ├── openeo.ts
│   │   └── h3.ts
│   │
│   ├── App.tsx                   # Root component
│   ├── main.tsx                  # Entry point
│   └── vite-env.d.ts            # Vite type definitions
│
├── tests/                        # Test files
│   ├── unit/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── utils/
│   ├── integration/
│   └── e2e/
│
├── .eslintrc.js                  # ESLint configuration
├── .prettierrc                   # Prettier configuration
├── tailwind.config.js            # Tailwind configuration
├── postcss.config.js             # PostCSS configuration
├── tsconfig.json                 # TypeScript configuration
├── vite.config.ts                # Vite configuration
├── jest.config.js                # Jest configuration
├── package.json                  # Dependencies
├── package-lock.json             # Lock file
└── README.md                     # Frontend README
```

## 5. API Layer Structure

```text
api/                              # API Gateway & Documentation
│
├── gateway/                      # API Gateway service
│   ├── src/
│   │   ├── routes/              # Route definitions
│   │   │   ├── v1/
│   │   │   │   ├── farmers.ts
│   │   │   │   ├── policies.ts
│   │   │   │   ├── onboarding.ts
│   │   │   │   ├── verification.ts
│   │   │   │   ├── claims.ts
│   │   │   │   ├── payments.ts
│   │   │   │   ├── oracles.ts
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   ├── middleware/          # Gateway middleware
│   │   │   ├── auth.ts
│   │   │   ├── rateLimit.ts
│   │   │   ├── validation.ts
│   │   │   ├── logging.ts
│   │   │   └── cors.ts
│   │   ├── controllers/         # Request handlers
│   │   ├── services/            # Business logic
│   │   ├── validators/          # Request validation
│   │   ├── utils/               # Utilities
│   │   ├── config/              # Configuration
│   │   └── server.ts            # Server entry point
│   ├── tests/
│   ├── package.json
│   └── tsconfig.json
│
├── docs/                         # API Documentation
│   ├── openapi/                 # OpenAPI specifications
│   │   ├── v1/
│   │   │   ├── openapi.yaml    # Main spec
│   │   │   ├── schemas/        # Schema definitions
│   │   │   │   ├── farmer.yaml
│   │   │   │   ├── policy.yaml
│   │   │   │   ├── onboarding.yaml
│   │   │   │   └── ...
│   │   │   ├── paths/          # Path definitions
│   │   │   │   ├── farmers.yaml
│   │   │   │   ├── policies.yaml
│   │   │   │   └── ...
│   │   │   └── components/     # Reusable components
│   │   │       ├── securitySchemes.yaml
│   │   │       ├── parameters.yaml
│   │   │       └── responses.yaml
│   │   └── README.md
│   │
│   ├── postman/                 # Postman collections
│   │   ├── BimaGrid API.postman_collection.json
│   │   ├── BimaGrid API.postman_environment.json
│   │   └── README.md
│   │
│   └── guides/                  # API usage guides
│       ├── getting-started.md
│       ├── authentication.md
│       ├── webhooks.md
│       ├── rate-limiting.md
│       └── error-handling.md
│
├── sdks/                         # Client SDKs
│   ├── python/                  # Python SDK
│   │   ├── bimagrid/
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   ├── models.py
│   │   │   └── exceptions.py
│   │   ├── setup.py
│   │   └── README.md
│   │
│   ├── javascript/              # JavaScript SDK
│   │   ├── src/
│   │   │   ├── index.ts
│   │   │   ├── client.ts
│   │   │   └── types.ts
│   │   ├── package.json
│   │   └── README.md
│   │
│   └── README.md
│
├── examples/                     # API usage examples
│   ├── python/
│   │   ├── register_farmer.py
│   │   ├── create_policy.py
│   │   └── check_claim.py
│   ├── javascript/
│   │   ├── registerFarmer.js
│   │   ├── createPolicy.js
│   │   └── checkClaim.js
│   └── curl/
│       ├── register_farmer.sh
│       ├── create_policy.sh
│       └── check_claim.sh
│
└── README.md
```

## 6. USSD Layer Structure

```text
ussd/                             # USSD Gateway Service
│
├── src/                          # Source code
│   │
│   ├── gateway/                  # USSD gateway handler
│   │   ├── __init__.py
│   │   ├── views.py             # HTTP endpoint for Africa's Talking
│   │   ├── urls.py              # URL routing
│   │   ├── middleware.py        # Request validation
│   │   └── serializers.py       # Request/response parsing
│   │
│   ├── flows/                    # USSD flow definitions
│   │   ├── __init__.py
│   │   ├── base.py              # Base flow class
│   │   ├── registration.py      # Farmer registration flow
│   │   │   ├── __init__.py
│   │   │   ├── screens.py       # Screen definitions
│   │   │   ├── validators.py    # Input validation
│   │   │   └── handlers.py      # Screen handlers
│   │   ├── policy_status.py     # Check policy status
│   │   ├── claims.py            # File claim flow
│   │   ├── payments.py          # Premium payment flow
│   │   └── support.py           # Help & support
│   │
│   ├── state/                    # Session state management
│   │   ├── __init__.py
│   │   ├── manager.py           # State manager
│   │   ├── models.py            # State models
│   │   └── storage.py           # State persistence (Redis)
│   │
│   ├── screens/                  # Screen rendering
│   │   ├── __init__.py
│   │   ├── renderer.py          # Screen renderer
│   │   ├── templates/           # Screen templates
│   │   │   ├── welcome.txt
│   │   │   ├── menu.txt
│   │   │   ├── input.txt
│   │   │   └── confirmation.txt
│   │   └── formatters.py        # Text formatting
│   │
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── farmer_service.py    # Farmer operations
│   │   ├── policy_service.py    # Policy operations
│   │   ├── payment_service.py   # Payment operations
│   │   └── notification_service.py
│   │
│   ├── integrations/             # External integrations
│   │   ├── __init__.py
│   │   ├── africastalking.py    # Africa's Talking API
│   │   ├── mpesa.py             # M-Pesa integration
│   │   └── backend_api.py       # Backend API client
│   │
│   ├── utils/                    # Utilities
│   │   ├── __init__.py
│   │   ├── validators.py        # Input validators
│   │   ├── formatters.py        # Data formatters
│   │   └── constants.py         # USSD constants
│   │
│   └── config/                   # Configuration
│       ├── __init__.py
│       ├── settings.py          # USSD settings
│       └── flows.py             # Flow configuration
│
├── tests/                        # Tests
│   ├── __init__.py
│   ├── test_flows/
│   │   ├── test_registration.py
│   │   ├── test_policy_status.py
│   │   └── test_claims.py
│   ├── test_state/
│   ├── test_services/
│   └── conftest.py
│
├── docs/                         # Documentation
│   ├── flow_diagrams/           # USSD flow diagrams
│   │   ├── registration.mermaid
│   │   ├── policy_status.mermaid
│   │   └── claims.mermaid
│   ├── screen_specs.md          # Screen specifications
│   └── user_guide.md            # User guide
│
├── requirements/                 # Dependencies
│   ├── base.txt
│   └── testing.txt
│
├── manage.py                     # Django management
├── pytest.ini                    # Pytest config
└── README.md                     # USSD README
```

## 7. Oracle Node Structure (Rust)

```text
oracle-node/                      # Rust Oracle Node
│
├── src/                          # Source code
│   │
│   ├── main.rs                   # Entry point
│   ├── lib.rs                    # Library root
│   │
│   ├── scheduler/                # Scheduling module
│   │   ├── mod.rs
│   │   ├── cron.rs              # Cron-like scheduling
│   │   ├── interval.rs          # Interval-based scheduling
│   │   └── event_listener.rs    # Blockchain event listener
│   │
│   ├── ingestion/                # Data ingestion module
│   │   ├── mod.rs
│   │   ├── sources/             # Data sources
│   │   │   ├── mod.rs
│   │   │   ├── chirps.rs        # CHIRPS rainfall data
│   │   │   ├── nasa_power.rs    # NASA POWER temperature
│   │   │   ├── open_meteo.rs    # Open-Meteo weather
│   │   │   ├── sentinel.rs      # Sentinel satellite data
│   │   │   └── local_station.rs # Local weather stations
│   │   ├── parsers/             # Response parsers
│   │   │   ├── mod.rs
│   │   │   ├── json.rs
│   │   │   └── xml.rs
│   │   ├── normalizers/         # Data normalization
│   │   │   ├── mod.rs
│   │   │   ├── rainfall.rs
│   │   │   ├── temperature.rs
│   │   │   └── indices.rs
│   │   └── aggregator.rs        # Multi-source aggregation
│   │
│   ├── crypto/                   # Cryptographic module
│   │   ├── mod.rs
│   │   ├── signing.rs           # ECDSA signing
│   │   ├── hashing.rs           # Keccak-256 hashing
│   │   ├── keys.rs              # Key management
│   │   └── verification.rs      # Signature verification
│   │
│   ├── blockchain/               # Blockchain interaction
│   │   ├── mod.rs
│   │   ├── provider.rs          # JSON-RPC provider
│   │   ├── contracts/           # Contract bindings
│   │   │   ├── mod.rs
│   │   │   ├── oracle.rs        # Oracle contract
│   │   │   └── policy.rs        # Policy contract
│   │   ├── transactions.rs      # Transaction building
│   │   └── events.rs            # Event listening
│   │
│   ├── consensus/                # Consensus logic
│   │   ├── mod.rs
│   │   ├── median.rs            # Median calculation
│   │   ├── threshold.rs         # Threshold evaluation
│   │   └── validation.rs        # Data validation
│   │
│   ├── api/                      # God Mode admin API
│   │   ├── mod.rs
│   │   ├── server.rs            # Axum server
│   │   ├── routes.rs            # Route definitions
│   │   ├── handlers.rs          # Request handlers
│   │   └── middleware.rs        # Auth middleware
│   │
│   ├── config/                   # Configuration
│   │   ├── mod.rs
│   │   ├── settings.rs          # Settings struct
│   │   └── validation.rs        # Config validation
│   │
│   ├── errors/                   # Error types
│   │   ├── mod.rs
│   │   └── types.rs
│   │
│   └── utils/                    # Utilities
│       ├── mod.rs
│       ├── time.rs              # Time utilities
│       ├── retry.rs             # Retry logic
│       └── logging.rs           # Logging setup
│
├── tests/                        # Integration tests
│   ├── integration/
│   │   ├── test_ingestion.rs
│   │   ├── test_crypto.rs
│   │   ├── test_blockchain.rs
│   │   └── test_consensus.rs
│   └── fixtures/
│       ├── weather_data.json
│       └── blockchain_responses.json
│
├── benches/                      # Benchmarks
│   ├── ingestion_bench.rs
│   ├── crypto_bench.rs
│   └── consensus_bench.rs
│
├── examples/                     # Usage examples
│   ├── basic_oracle.rs
│   └── multi_source.rs
│
├── config/                       # Configuration files
│   ├── oracle-1.toml
│   ├── oracle-2.toml
│   └── oracle-3.toml
│
├── scripts/                      # Utility scripts
│   ├── generate_keys.sh
│   └── deploy.sh
│
├── Cargo.toml                    # Rust dependencies
├── Cargo.lock                    # Lock file
├── rustfmt.toml                  # Formatter config
├── clippy.toml                   # Linter config
└── README.md                     # Oracle README
```

## 8. Smart Contract Structure

```text
contracts/                        # Solidity Smart Contracts
│
├── contracts/                    # Contract source code
│   │
│   ├── core/                     # Core contracts
│   │   ├── KilimaShieldOracle.sol      # Oracle data receiver
│   │   ├── PolicyRegistry.sol          # Policy management
│   │   ├── EscrowVault.sol             # Premium escrow
│   │   └── MitigationVerifier.sol      # Discount validation
│   │
│   ├── interfaces/               # Contract interfaces
│   │   ├── IOracle.sol
│   │   ├── IPolicy.sol
│   │   ├── IEscrow.sol
│   │   └── IVerification.sol
│   │
│   ├── libraries/                # Reusable libraries
│   │   ├── Math.sol             # Math utilities
│   │   ├── ECDSA.sol            # Signature verification
│   │   ├── MerkleProof.sol      # Merkle proof verification
│   │   └── H3.sol               # H3 spatial indexing
│   │
│   ├── mocks/                    # Mock contracts for testing
│   │   ├── MockOracle.sol
│   │   ├── MockToken.sol
│   │   └── MockWeatherFeed.sol
│   │
│   └── tokens/                   # Token contracts
│       ├── PolicyNFT.sol        # Policy NFT (optional)
│       └── BimaToken.sol        # Governance token (optional)
│
├── scripts/                      # Deployment scripts
│   ├── deploy.js                # Main deployment script
│   ├── deploy-oracle.js         # Deploy oracle contract
│   ├── deploy-policy.js         # Deploy policy contract
│   ├── deploy-escrow.js         # Deploy escrow contract
│   ├── upgrade.js               # Upgrade contracts
│   └── verify.js                # Verify on block explorer
│
├── test/                         # Test files
│   ├── core/
│   │   ├── KilimaShieldOracle.test.js
│   │   ├── PolicyRegistry.test.js
│   │   ├── EscrowVault.test.js
│   │   └── MitigationVerifier.test.js
│   ├── integration/
│   │   ├── full-lifecycle.test.js
│   │   └── multi-oracle.test.js
│   └── helpers/
│       ├── fixtures.js          # Test fixtures
│       ├── time.js              # Time manipulation
│       └── signatures.js        # Signature helpers
│
├── tasks/                        # Hardhat tasks
│   ├── accounts.js              # List accounts
│   ├── balance.js               # Check balance
│   └── interact.js              # Contract interaction
│
├── deployments/                  # Deployment artifacts
│   ├── localhost/
│   ├── goerli/
│   └── mainnet/
│
├── utils/                        # Utility functions
│   ├── helpers.js
│   └── constants.js
│
├── abi/                          # Contract ABIs
│   ├── KilimaShieldOracle.json
│   ├── PolicyRegistry.json
│   ├── EscrowVault.json
│   └── MitigationVerifier.json
│
├── typechain/                    # TypeScript bindings
│   ├── KilimaShieldOracle.ts
│   ├── PolicyRegistry.ts
│   ├── EscrowVault.ts
│   └── MitigationVerifier.ts
│
├── coverage/                     # Test coverage reports
│
├── gas-report/                   # Gas usage reports
│
├── hardhat.config.js             # Hardhat configuration
├── .solhint.json                 # Solhint configuration
├── .prettierrc                   # Prettier configuration
├── package.json                  # Dependencies
├── package-lock.json             # Lock file
└── README.md                     # Contracts README
```

## 9. Infrastructure Structure

```text
infrastructure/                   # Infrastructure as Code
│
├── terraform/                    # Terraform configurations
│   │
│   ├── environments/             # Environment-specific configs
│   │   ├── dev/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   ├── terraform.tfvars
│   │   │   └── backend.tf
│   │   ├── staging/
│   │   │   └── ...
│   │   └── production/
│   │       └── ...
│   │
│   ├── modules/                  # Reusable modules
│   │   ├── vpc/                 # VPC module
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   └── README.md
│   │   ├── ecs/                 # ECS cluster module
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   └── README.md
│   │   ├── rds/                 # RDS database module
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   └── README.md
│   │   ├── s3/                  # S3 bucket module
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   └── README.md
│   │   ├── cloudfront/          # CloudFront CDN module
│   │   │   └── ...
│   │   ├── route53/             # Route53 DNS module
│   │   │   └── ...
│   │   └── secrets/             # Secrets Manager module
│   │       └── ...
│   │
│   ├── global/                   # Global resources
│   │   ├── dns.tf               # DNS configuration
│   │   ├── iam.tf               # IAM roles and policies
│   │   └── ssl.tf               # SSL certificates
│   │
│   ├── main.tf                   # Root module
│   ├── variables.tf              # Root variables
│   ├── outputs.tf                # Root outputs
│   ├── providers.tf              # Provider configuration
│   └── versions.tf               # Version constraints
│
├── docker/                       # Docker configurations
│   │
│   ├── docker-compose.yml        # Development compose
│   ├── docker-compose.dev.yml    # Dev overrides
│   ├── docker-compose.prod.yml   # Production overrides
│   │
│   ├── Dockerfiles/              # Dockerfiles
│   │   ├── backend.dockerfile
│   │   ├── frontend.dockerfile
│   │   ├── oracle.dockerfile
│   │   ├── ussd.dockerfile
│   │   └── nginx.dockerfile
│   │
│   └── configs/                  # Config files for containers
│       ├── nginx/
│       │   ├── nginx.conf
│       │   └── conf.d/
│       ├── postgres/
│       │   └── postgresql.conf
│       └── redis/
│           └── redis.conf
│
├── ansible/                      # Ansible playbooks
│   ├── playbooks/
│   │   ├── deploy-backend.yml
│   │   ├── deploy-oracle.yml
│   │   ├── setup-server.yml
│   │   └── backup.yml
│   ├── inventory/
│   │   ├── dev.ini
│   │   ├── staging.ini
│   │   └── production.ini
│   ├── roles/
│   │   ├── common/
│   │   ├── docker/
│   │   ├── nginx/
│   │   └── monitoring/
│   └── group_vars/
│       ├── all.yml
│       ├── dev.yml
│       └── production.yml
│
├── kubernetes/                   # Kubernetes manifests
│   ├── base/                    # Base manifests
│   │   ├── backend/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── configmap.yaml
│   │   ├── frontend/
│   │   ├── oracle/
│   │   └── ingress.yaml
│   ├── overlays/                # Environment overlays
│   │   ├── dev/
│   │   ├── staging/
│   │   └── production/
│   └── helm/                    # Helm charts
│       ├── bimagrid/
│       │   ├── Chart.yaml
│       │   ├── values.yaml
│       │   └── templates/
│       └── dependencies/
│
├── scripts/                      # Infrastructure scripts
│   ├── setup-aws.sh
│   ├── deploy.sh
│   ├── rollback.sh
│   └── cleanup.sh
│
└── README.md
```

## 10. Documentation Structure

```text
docs/                             # Project Documentation
│
├── architecture/                 # Architecture documentation
│   ├── overview.md              # System overview
│   ├── components.md            # Component details
│   ├── data-flow.md             # Data flow diagrams
│   ├── deployment.md            # Deployment architecture
│   └── diagrams/
│       ├── system-architecture.png
│       ├── data-flow.png
│       └── deployment.png
│
├── api/                          # API documentation
│   ├── rest-api.md              # REST API guide
│   ├── ussd-api.md              # USSD API guide
│   ├── webhooks.md              # Webhook documentation
│   ├── authentication.md        # Auth guide
│   └── openapi/                 # OpenAPI specs
│       └── openapi.yaml
│
├── development/                  # Development guides
│   ├── getting-started.md       # Quick start guide
│   ├── setup.md                 # Detailed setup
│   ├── coding-standards.md      # Code standards
│   ├── testing.md               # Testing guide
│   ├── debugging.md             # Debugging tips
│   └── troubleshooting.md       # Common issues
│
├── deployment/                   # Deployment guides
│   ├── local.md                 # Local deployment
│   ├── staging.md               # Staging deployment
│   ├── production.md            # Production deployment
│   ├── rollback.md              # Rollback procedures
│   └── monitoring.md            # Monitoring setup
│
├── operations/                   # Operations guides
│   ├── backup.md                # Backup procedures
│   ├── recovery.md              # Disaster recovery
│   ├── scaling.md               # Scaling guide
│   ├── security.md              # Security procedures
│   └── incident-response.md     # Incident response
│
├── user-guides/                  # User documentation
│   ├── farmer-guide.md          # Farmer user guide
│   ├── agent-guide.md           # Agent user guide
│   ├── admin-guide.md           # Admin user guide
│   └── faq.md                   # Frequently asked questions
│
├── business/                     # Business documentation
│   ├── product-vision.md        # Product vision
│   ├── market-analysis.md       # Market analysis
│   ├── competitive-analysis.md  # Competitor analysis
│   ├── go-to-market.md          # GTM strategy
│   └── financial-model.md       # Financial projections
│
├── compliance/                   # Compliance documentation
│   ├── ira-requirements.md      # IRA regulatory requirements
│   ├── data-protection.md       # Data protection (GDPR, etc.)
│   ├── kyc-aml.md               # KYC/AML procedures
│   └── audit-procedures.md      # Audit procedures
│
├── research/                     # Research documentation
│   ├── actuarial-model.md       # Actuarial model
│   ├── basis-risk.md            # Basis risk analysis
│   ├── satellite-data.md        # Satellite data usage
│   └── oracle-design.md         # Oracle design
│
├── diagrams/                     # Diagrams and visuals
│   ├── architecture/
│   ├── flowcharts/
│   ├── sequence-diagrams/
│   └── entity-relationship/
│
├── glossary.md                   # Glossary of terms
├── changelog.md                  # Version changelog
├── roadmap.md                    # Product roadmap
└── README.md                     # Documentation index
```

## 11. Development Pipeline

The BimaGrid development pipeline follows a structured workflow from ideation to production deployment.

### Phase 1: Planning & Design

1. Feature Request / Bug Report
   - Created via GitHub Issues
   - Tagged with appropriate labels (feature, bug, enhancement)
   - Assigned to product owner for triage

2. Triage & Prioritization
   - Product owner reviews and prioritizes
   - Added to appropriate sprint backlog
   - Estimated in story points

3. Technical Design
   - Architecture Decision Record (ADR) created if needed
   - Technical design document written
   - API contracts defined (OpenAPI specs)
   - Database schema changes planned
   - Security considerations documented

4. Design Review
   - Technical lead reviews design
   - Team provides feedback
   - Design approved or revised

### Phase 2: Development

1. Branch Creation
   - Branch created from main: feature/TICKET-123-description
   - Naming convention: feature/, fix/, hotfix/, refactor/

2. Local Development
   - Developer sets up local environment
   - Writes code following coding standards
   - Writes unit tests (minimum 80% coverage)
   - Runs pre-commit hooks
   - Commits with conventional commit messages

3. Code Review
   - Developer creates Pull Request
   - PR description includes:
     - Summary of changes
     - Testing performed
     - Screenshots (if UI changes)
     - Breaking changes (if any)
   - Automated checks run (CI)
   - Minimum 2 approvals required
   - All conversations resolved

4. Integration Testing
   - Code merged to develop branch
   - Integration tests run
   - QA team performs manual testing
   - Bugs fixed and retested

### Phase 3: Staging

1. Staging Deployment
   - Code merged to staging branch
   - Automated deployment to staging environment
   - Smoke tests run
   - Performance tests run

2. User Acceptance Testing (UAT)
   - Product owner tests features
   - Stakeholders review
   - Feedback collected and addressed

3. Security Audit
   - Automated security scans run
   - Manual security review for critical changes
   - Penetration testing (quarterly)

### Phase 4: Production

1. Release Preparation
   - Release branch created from staging
   - Release notes written
   - Database migrations prepared
   - Rollback plan documented

2. Production Deployment
   - Deployment scheduled (low-traffic window)
   - Blue-green deployment executed
   - Health checks verified
   - Monitoring alerts configured

3. Post-Deployment
   - Smoke tests run in production
   - Monitoring dashboards reviewed
   - Team on standby for 2 hours
   - Stakeholders notified

4. Documentation
   - User documentation updated
   - API documentation updated
   - Changelog updated
   - Version tags created

### Phase 5: Monitoring & Maintenance

1. Monitoring
   - Application metrics tracked
   - Error rates monitored
   - Performance metrics reviewed
   - User feedback collected

2. Incident Response
   - Incidents logged
   - Root cause analysis performed
   - Post-mortem documented
   - Preventive measures implemented

3. Continuous Improvement
   - Retrospectives held (bi-weekly)
   - Technical debt tracked
   - Process improvements implemented
   - Team skills developed

## 12. Git Workflow

### Branching Strategy: GitFlow

### Main Branches

- main: Production-ready code (protected)
- develop: Integration branch for features (protected)

### Supporting Branches

- feature/*: New features (from develop, merge to develop)
- release/*: Release preparation (from develop, merge to main & develop)
- hotfix/*: Emergency fixes (from main, merge to main & develop)
- bugfix/*: Bug fixes (from develop, merge to develop)

### Branch Naming Convention

- feature/TICKET-123-add-farmer-onboarding
- fix/TICKET-456-resolve-oracle-timeout
- hotfix/TICKET-789-critical-payment-bug
- release/v1.2.0
- refactor/TICKET-101-optimize-queries

### Commit Message Format (Conventional Commits)

```text
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Formatting, no code logic change
- refactor: Code change that neither fixes a bug nor adds a feature
- test: Adding missing tests or correcting existing tests
- chore: Changes to build process or auxiliary tools

### Scopes

- backend, frontend, oracle, contracts, ussd, infra, docs

### Examples

- feat(backend): add farmer onboarding API endpoint
- fix(oracle): resolve timeout issue with CHIRPS API
- docs(contracts): update deployment instructions
- test(frontend): add unit tests for policy form

### Pull Request Process

1. Create PR from feature branch to develop
2. Fill out PR template completely
3. Request reviews from 2 team members
4. Address all review comments
5. Ensure CI passes
6. Squash and merge

### Merge Strategy

- feature → develop: Squash and merge
- develop → staging: Merge commit
- staging → main: Merge commit
- hotfix → main: Merge commit
- main → develop: Merge commit

### Tagging

- Semantic versioning: vMAJOR.MINOR.PATCH
- Tags created on main branch
- Automated changelog generation

## 13. CI/CD Pipeline

### Continuous Integration (CI)

#### Triggers

- Push to any branch
- Pull request creation/update

#### Stages

1. Lint & Format
   - Python: black, isort, flake8, mypy
   - JavaScript: ESLint, Prettier
   - Rust: clippy, rustfmt
   - Solidity: solhint

2. Build
   - Backend: Docker image build
   - Frontend: Next.js build
   - Oracle: Cargo build
   - Contracts: Hardhat compile

3. Test
   - Backend: pytest with coverage
   - Frontend: Jest + React Testing Library
   - Oracle: cargo test
   - Contracts: Hardhat test with coverage
   - Integration: pytest integration tests

4. Security Scan
   - Python: safety, bandit
   - JavaScript: npm audit, snyk
   - Rust: cargo-audit
   - Solidity: slither, mythril
   - Secrets: git-secrets, trufflehog

5. Quality Gates
   - Code coverage ≥ 80%
   - No critical vulnerabilities
   - No linting errors
   - All tests passing

### Continuous Deployment (CD)

#### Staging Deployment

Trigger: Merge to staging branch

1. Build Docker images
2. Push to AWS ECR
3. Update ECS task definitions
4. Deploy to staging ECS cluster
5. Run database migrations
6. Run smoke tests
7. Notify Slack channel

#### Production Deployment

Trigger: Manual approval after staging validation

1. Build production Docker images
2. Push to AWS ECR
3. Create database backup
4. Update ECS task definitions
5. Deploy to production ECS cluster (blue-green)
6. Run database migrations
7. Run smoke tests
8. Switch traffic to new deployment
9. Monitor for 30 minutes
10. Notify stakeholders

### Rollback Procedure

1. Identify issue via monitoring
2. Switch traffic to previous deployment
3. Investigate root cause
4. Fix and redeploy

### Environment Promotion

develop → staging → production

Each environment has:

- Separate database
- Separate Redis instance
- Separate S3 bucket
- Separate API keys
- Separate monitoring

## 14. Local Development Workflow

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Rust 1.74+
- PostgreSQL client tools
- Git

### Initial Setup

1. Clone repository

   ```text
   $ git clone https://github.com/your-org/bimagrid.git
   $ cd bimagrid
   ```

2. Run setup script

   ```text
   $ ./scripts/setup.sh
   ```

   This script:
   - Creates Python virtual environment
   - Installs Python dependencies
   - Installs Node dependencies
   - Installs Rust dependencies
   - Sets up pre-commit hooks
   - Creates .env file from template

3. Configure environment

   ```text
   $ cp .env.example .env
   $ vim .env
   ```

   Required variables:
   - DATABASE_URL
   - REDIS_URL
   - AFRICASTALKING_API_KEY
   - MPESA_CONSUMER_KEY
   - OPENEO_USERNAME
   - ORACLE_PRIVATE_KEY

4. Start infrastructure

   ```text
   $ docker-compose up -d postgres redis
   ```

5. Setup database

   ```text
   $ cd backend
   $ python manage.py migrate
   $ python manage.py seed_h3_grids
   $ python manage.py import_crop_risk_constants
   ```

6. Deploy contracts (local blockchain)

   ```text
   $ cd contracts
   $ npx hardhat node  # Terminal 1
   $ npx hardhat run scripts/deploy.js --network localhost  # Terminal 2
   ```

7. Start all services

   ```text
   $ cd ..
   $ docker-compose up
   ```

   Services started:
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000
   - Oracle: http://localhost:8080
   - USSD: http://localhost:8001
   - Admin: http://localhost:8000/admin

### Daily Workflow

1. Pull latest changes

   ```text
   $ git pull origin develop
   ```

2. Update dependencies

   ```text
   $ cd backend && pip install -r requirements/development.txt
   $ cd frontend && npm install
   $ cd oracle-node && cargo build
   ```

3. Start services

   ```text
   $ docker-compose up
   ```

4. Make changes
   - Edit code
   - Save files
   - Hot reload (frontend/backend)
   - Restart oracle if needed

5. Run tests

   ```text
   $ cd backend && pytest
   $ cd frontend && npm test
   $ cd oracle-node && cargo test
   ```

6. Commit changes

   ```text
   $ git add .
   $ git commit -m "feat(backend): add new feature"
   ```

7. Push and create PR

   ```text
   $ git push origin feature/my-feature
   ```

### Troubleshooting

Database connection issues:

```text
$ docker-compose restart postgres
$ docker-compose exec postgres psql -U bimagrid -d bimagrid
```

Redis connection issues:

```text
$ docker-compose restart redis
$ docker-compose exec redis redis-cli ping
```

Port conflicts:

```text
$ lsof -i :8000
$ kill -9 <PID>
```

Permission issues:

```text
$ sudo chown -R $USER:$USER .
```

## 15. Deployment Workflow

### Deployment Environments

1. Local Development
   - Docker Compose
   - SQLite or local PostgreSQL
   - Mock external APIs
   - No real payments

2. Development (dev.bimagrid.io)
   - Shared development environment
   - Real PostgreSQL
   - Sandbox APIs (Africa's Talking, M-Pesa)
   - Test blockchain

3. Staging (staging.bimagrid.io)
   - Production-like environment
   - Real PostgreSQL (separate instance)
   - Sandbox APIs with production-like data
   - Test blockchain with realistic load

4. Production (bimagrid.io)
   - High availability
   - Multi-AZ deployment
   - Real APIs
   - Production blockchain
   - Real payments

### Deployment Checklist

#### Pre-Deployment

□ All tests passing
□ Code reviewed and approved
□ Documentation updated
□ Database migrations tested
□ Rollback plan documented
□ Monitoring alerts configured
□ Stakeholders notified

#### Deployment

□ Database backup created
□ Services deployed
□ Migrations run
□ Smoke tests passed
□ Health checks green
□ Traffic switched
□ Monitoring reviewed

#### Post-Deployment

□ Application functional
□ Performance acceptable
□ Error rates normal
□ Stakeholders notified
□ Deployment documented

### Rollback Procedure

1. Identify issue
   - Monitor error rates
   - Check logs
   - Assess severity

2. Decide to rollback
   - Critical issue: Immediate rollback
   - Non-critical: Fix forward

3. Execute rollback

   ```text
   $ cd infrastructure
   $ ./scripts/rollback.sh <version>
   ```

4. Verify rollback
   - Run smoke tests
   - Check monitoring
   - Verify data integrity

5. Communicate
   - Notify stakeholders
   - Update status page
   - Document incident

## 16. Environment Management

### Environment Variables

All environment variables are managed through .env files and AWS Secrets Manager.

### Required Variables

#### Backend

- DJANGO_SETTINGS_MODULE
- SECRET_KEY
- DATABASE_URL
- REDIS_URL
- AFRICASTALKING_API_KEY
- AFRICASTALKING_USERNAME
- MPESA_CONSUMER_KEY
- MPESA_CONSUMER_SECRET
- MPESA_SHORTCODE
- OPENEO_BACKEND_URL
- OPENEO_USERNAME
- OPENEO_PASSWORD
- BLOCKCHAIN_RPC_URL
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- SENTRY_DSN

#### Oracle

- ORACLE_ID
- ORACLE_PRIVATE_KEY
- BLOCKCHAIN_RPC_URL
- CONTRACT_ADDRESS
- DATA_SOURCES
- EVALUATION_INTERVAL

#### Frontend

- REACT_APP_API_URL
- REACT_APP_MAPBOX_TOKEN
- REACT_APP_ENVIRONMENT

### Environment-Specific Configuration

#### Development

- DEBUG=True
- ALLOWED_HOSTS=['localhost', '127.0.0.1']
- Database: Local PostgreSQL
- Email: Console backend
- Storage: Local filesystem

#### Staging

- DEBUG=False
- ALLOWED_HOSTS=['staging.bimagrid.io']
- Database: RDS PostgreSQL (small instance)
- Email: SES (sandbox)
- Storage: S3 (staging bucket)

#### Production

- DEBUG=False
- ALLOWED_HOSTS=['bimagrid.io', 'www.bimagrid.io']
- Database: RDS PostgreSQL (large, Multi-AZ)
- Email: SES (production)
- Storage: S3 (production bucket)
- CDN: CloudFront

### Secret Management

#### Development

- .env files (gitignored)
- .env.example committed to repo

#### Staging/Production

- AWS Secrets Manager
- IAM roles for access
- Automatic rotation

Access pattern:

1. Application starts
2. Fetches secrets from Secrets Manager
3. Injects into environment
4. Application uses environment variables

## 17. Dependency Management

### Python Dependencies

Management: pip + requirements files

Files:

- requirements/base.txt: Core dependencies
- requirements/development.txt: Dev tools
- requirements/testing.txt: Test tools
- requirements/production.txt: Production optimizations

Update process:

```text
$ pip install -r requirements/base.txt
$ pip freeze > requirements/base.txt
```

Security scanning:

```text
$ safety check -r requirements/base.txt
```

### Node Dependencies

Management: npm + package.json

Files:

- package.json: Dependencies
- package-lock.json: Lock file

Update process:

```text
$ npm install
$ npm update
```

Security scanning:

```text
$ npm audit
$ npm audit fix
```

### Rust Dependencies

Management: Cargo + Cargo.toml

Files:

- Cargo.toml: Dependencies
- Cargo.lock: Lock file

Update process:

```text
$ cargo update
$ cargo build
```

Security scanning:

```text
$ cargo audit
```

### Solidity Dependencies

Management: npm + package.json

Files:

- package.json: Dependencies (OpenZeppelin, etc.)
- package-lock.json: Lock file

Update process:

```text
$ npm install
$ npm update
```

### Dependency Update Policy

- Critical security updates: Immediate
- Minor updates: Weekly
- Major updates: Monthly (with testing)
- All updates: Tested in staging before production

## 18. Code Review Process

### Review Requirements

- Minimum 2 approvals
- All conversations resolved
- CI passing
- Coverage ≥ 80%
- No critical vulnerabilities

### Review Checklist

#### Code Quality

□ Code follows style guide
□ Functions are small and focused
□ Variables are well-named
□ Comments explain "why", not "what"
□ No code duplication
□ Error handling is comprehensive

#### Architecture

□ Follows existing patterns
□ No unnecessary complexity
□ Proper separation of concerns
□ Dependencies are appropriate
□ Performance considerations addressed

#### Security

□ No hardcoded secrets
□ Input validation present
□ SQL injection prevented
□ XSS prevention in place
□ Authentication/authorization correct
□ Sensitive data protected

#### Testing

□ Unit tests written
□ Edge cases covered
□ Integration tests added (if needed)
□ Tests are readable and maintainable

#### Documentation

□ Docstrings added
□ README updated (if needed)
□ API docs updated (if needed)
□ Complex logic explained

### Review Feedback Guidelines

Be constructive:

✓ "Consider extracting this into a helper function for reusability"
✗ "This is bad code"

Be specific:

✓ "This query could be optimized by adding an index on user_id"
✗ "This is slow"

Ask questions:

✓ "What happens if the API returns null here?"
✗ "This will break"

Suggest, don't demand:

✓ "Would it make sense to use a constant here?"
✗ "Use a constant here"

Acknowledge good work:

✓ "Great use of the strategy pattern here!"

## 19. Release Process

### Release Types

1. Major (v2.0.0): Breaking changes
2. Minor (v1.2.0): New features, backward compatible
3. Patch (v1.2.3): Bug fixes, backward compatible

### Release Workflow

1. Create release branch

   ```text
   $ git checkout -b release/v1.2.0 develop
   ```

2. Update version numbers
   - backend/__init__.py
   - frontend/package.json
   - oracle-node/Cargo.toml
   - contracts/package.json

3. Update changelog

   ```text
   $ git-changelog > CHANGELOG.md
   ```

4. Test thoroughly
   - All tests passing
   - Manual testing completed
   - Performance testing done

5. Create release PR
   - From release/v1.2.0 to main
   - Title: "Release v1.2.0"
   - Description: Summary of changes

6. Merge to main
   - Squash and merge
   - Tag: v1.2.0

7. Deploy to production
   - Follow deployment workflow

8. Merge back to develop

   ```text
   $ git checkout develop
   $ git merge main
   ```

9. Create GitHub release
   - Title: v1.2.0
   - Tag: v1.2.0
   - Release notes from changelog
   - Attach artifacts (if any)

10. Communicate
    - Notify stakeholders
    - Update status page
    - Send email to users (if major)

### Release Notes Template

```markdown
## What's Changed

### New Features
- Feature 1 description
- Feature 2 description

### Bug Fixes
- Fix 1 description
- Fix 2 description

### Breaking Changes
- Breaking change 1 (migration guide)

### Performance Improvements
- Improvement 1 description

### Security
- Security fix 1 description

### Documentation
- Doc update 1 description

## Upgrade Guide
(If major version, include migration steps)

## Contributors
Thanks to @user1, @user2 for their contributions!
```

## 20. Incident Response Workflow

### Incident Severity Levels

#### SEV-1 (Critical)

- Complete service outage
- Data loss or corruption
- Security breach
- Response time: Immediate
- Resolution time: < 1 hour

#### SEV-2 (High)

- Major feature unavailable
- Significant performance degradation
- Partial data loss
- Response time: < 15 minutes
- Resolution time: < 4 hours

#### SEV-3 (Medium)

- Minor feature unavailable
- Minor performance issues
- No data loss
- Response time: < 1 hour
- Resolution time: < 24 hours

#### SEV-4 (Low)

- Cosmetic issues
- Minor bugs
- Response time: < 4 hours
- Resolution time: < 1 week

### Incident Response Process

1. Detection
   - Automated alert (monitoring)
   - User report (support ticket)
   - Internal observation

2. Triage
   - Assess severity
   - Assign incident commander
   - Create incident channel (Slack)
   - Page on-call if SEV-1/2

3. Investigation
   - Gather logs and metrics
   - Identify root cause
   - Assess impact
   - Document findings

4. Mitigation
   - Implement temporary fix
   - Restore service
   - Verify resolution
   - Monitor for recurrence

5. Resolution
   - Implement permanent fix
   - Test thoroughly
   - Deploy to production
   - Verify long-term stability

6. Communication
   - Update status page
   - Notify stakeholders
   - Send user communications (if needed)

7. Post-Mortem
   - Schedule within 48 hours
   - Document timeline
   - Identify root cause
   - List action items
   - Assign owners
   - Share with team

### Post-Mortem Template

```markdown
# Incident Post-Mortem: [Incident Title]

## Summary
Brief description of the incident

## Impact
- Duration: X hours
- Users affected: X
- Data affected: X
- Revenue impact: $X

## Timeline
- HH:MM - Incident detected
- HH:MM - Investigation started
- HH:MM - Root cause identified
- HH:MM - Mitigation implemented
- HH:MM - Service restored
- HH:MM - Incident resolved

## Root Cause
Detailed explanation of what went wrong

## Resolution
Steps taken to fix the issue

## Prevention
Action items to prevent recurrence:
- [ ] Action 1 (Owner: @user, Due: YYYY-MM-DD)
- [ ] Action 2 (Owner: @user, Due: YYYY-MM-DD)

## Lessons Learned
What went well, what could be improved
```

## End of Document
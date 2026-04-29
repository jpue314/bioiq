# BioIQ — Core Platform Design Spec
**Date:** 2026-04-29
**Sub-project:** 1 of 7 — Core Platform
**Status:** Approved

---

## Overview

BioIQ is a centralized personal health information hub. Instead of visiting multiple portals (Whoop, Apple Health, Garmin, physician patient portals), users see all their health data and a synthesized daily readiness score in one place. The platform is HIPAA-compliant, AI-powered, and designed with an Apple-quality, Wix-inspired aesthetic.

**Initial users:** Personal use + family testing
**Target:** Multi-user SaaS product for public release

---

## Sub-project Roadmap

| # | Sub-project | Depends On |
|---|-------------|------------|
| 1 | **Core Platform** (this spec) | - |
| 2 | Device & Service Integrations | 1 |
| 3 | Health Dashboard | 1, 2 |
| 4 | AI Workout Generator | 1, 2, 3 |
| 5 | Health Records & HIPAA Communications | 1 |
| 6 | Mobile App (React Native/Expo) | 1, 2, 3 |
| 7 | Provider Portal | 1, 5 |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend API | Django 5.x + Django REST Framework |
| Web Frontend | Next.js 14 (App Router) |
| Mobile | React Native / Expo |
| Database | PostgreSQL (AWS RDS db.t3.micro) |
| File Storage | AWS S3 |
| Email | AWS SES |
| Backend Hosting | AWS EC2 t2.micro (free tier) |
| Frontend Hosting | Vercel (free tier) |
| AI | Anthropic Claude API (Haiku + Sonnet) |
| Auth (social) | Sign in with Apple, Sign in with Google |

---

## Architecture

```
+-----------------------------------------------------+
|                    USERS                            |
|         Browser           iPhone App               |
+------------+------------------+--------------------+
             |                  |
     +-------+------+   +-------+------+
     |  Next.js     |   | React Native |
     |  (Vercel)    |   |   (Expo)     |
     +-------+------+   +-------+------+
             |                  |
             +--------+---------+
                      | HTTPS REST API
             +--------+---------+
             |   Django + DRF   |  <- EC2 t2.micro (AWS)
             |   (API Server)   |
             +--------+---------+
                      |
          +-----------+-----------+
          |           |           |
    +-----+-----+ +---+---+ +----+----+
    | PostgreSQL| |  S3   | |  SES    |
    | (RDS)     | |(Files)| |(Email)  |
    +-----------+ +-------+ +---------+
```

Key principles:
- Django is the single source of truth. All PHI lives within the AWS HIPAA boundary.
- Next.js and React Native are thin clients. They display data, never store PHI.
- Vercel hosts only the Next.js frontend. No health data ever touches Vercel infrastructure.
- AWS BAA (Business Associate Agreement) signed before any real user data is stored.

---

## Data Model

### User
```
id, email, password_hash
first_name, last_name
is_active, is_verified
created_at, updated_at
```

### HealthProfile (one per User)
```
date_of_birth, biological_sex
height, weight
fitness_goals             -- e.g. "lose weight", "build endurance"
medical_conditions        -- encrypted at field level (PHI)
```

### DailyScore (one per User per day)
```
date
readiness_score           -- 0-100, synthesized from all sources
sleep_score, recovery_score, activity_score
score_breakdown           -- JSON: what drove the number
```

### ConnectedDevice (many per User)
```
provider                  -- whoop | apple_health | garmin | fitbit | strava
access_token              -- encrypted
refresh_token             -- encrypted
last_synced_at
```

### HealthMetric (raw data points, many per User)
```
source                    -- ConnectedDevice FK
metric_type               -- hrv | resting_hr | steps | sleep_duration | ...
value, unit
recorded_at
```

### ProviderAccess (many per User)
```
patient                   -- User FK
provider_name, provider_email, provider_type
access_level              -- read_summary | read_full | read_metrics
authorized_at, expires_at
revoked_at                -- patient can revoke at any time
```

### AuditLog (HIPAA requirement)
```
user                      -- User FK (whose data)
actor                     -- User FK (who accessed it)
action                    -- read | write | delete | share
resource_type, resource_id
ip_address, user_agent
timestamp
```

### AIConversation
```
user                      -- User FK
messages                  -- JSON array of {role, content, timestamp}
conversation_type         -- chat | insights | questions | workout
model_used                -- claude-haiku-4-5 | claude-sonnet-4-6
created_at, updated_at
```

---

## Authentication

Flow:
1. User registers with email/password or social login
2. Django validates credentials, issues JWT access token (15 min) + refresh token (30 days, httpOnly cookie)
3. Every API request carries the JWT. Django validates on each call.
4. Refresh tokens rotate silently. Users stay logged in without re-authenticating.

Supported methods at launch:
- Email + password
- Sign in with Apple (required by Apple if any other social login is offered on iOS)
- Sign in with Google

Planned future:
- Passkeys / Face ID biometric re-auth on mobile

---

## Security & HIPAA Controls

| Control | Implementation |
|---|---|
| Data in transit | HTTPS everywhere (TLS 1.2+), enforced at AWS ALB |
| Data at rest | RDS encryption enabled, S3 server-side encryption (AES-256) |
| Field-level encryption | PHI fields encrypted with django-encrypted-fields |
| Audit logging | Every PHI read/write logged to AuditLog (HIPAA 164.312) |
| Session management | Refresh token rotation + revocation on logout |
| Password policy | Min 12 chars, bcrypt hashing (Django default) |
| Provider access consent | Patient must explicitly grant; revocable at any time |
| Right to erasure | Account deletion cascade-wipes all PHI |
| BAA | AWS BAA signed before production data stored |

---

## API Design

```
AUTH
POST   /api/auth/register/
POST   /api/auth/login/
POST   /api/auth/logout/
POST   /api/auth/token/refresh/
POST   /api/auth/social/apple/
POST   /api/auth/social/google/
POST   /api/auth/password/reset/

USER & PROFILE
GET    /api/me/
PATCH  /api/me/
DELETE /api/me/                     -- cascade-wipes all PHI

DASHBOARD
GET    /api/scores/today/           -- readiness score + breakdown (cached)
GET    /api/scores/?start=&end=     -- score history

HEALTH METRICS
GET    /api/metrics/?type=&start=&end=
POST   /api/metrics/                -- internal ingestion only

CONNECTED DEVICES
GET    /api/devices/
POST   /api/devices/connect/        -- initiate OAuth server-side
DELETE /api/devices/{id}/

PROVIDER ACCESS
GET    /api/provider-access/
POST   /api/provider-access/
DELETE /api/provider-access/{id}/   -- revoke

AI
POST   /api/ai/chat/                -- routes to Claude Haiku (fast)
GET    /api/ai/chat/history/
POST   /api/ai/insights/            -- routes to Claude Sonnet (deep analysis)
POST   /api/ai/questions/           -- compile appointment questions
POST   /api/ai/workout/plan/        -- generate workout plan
```

All endpoints require authentication except register, login, token/refresh, password/reset.

---

## AI Layer

Provider: Anthropic Claude API
Brand: "BioIQ AI" -- users never see model names

| Task | Model | Reason |
|------|-------|--------|
| Chat, Q&A | Claude Haiku | Fast, low latency, low cost |
| Health insights | Claude Sonnet | Deep reasoning, nuanced analysis |
| Appointment question compilation | Claude Haiku | Fast, structured output |
| Workout plan generation | Claude Sonnet | Complex multi-variable reasoning |

Context injection: Every AI call receives the user HealthProfile + last 7 days of DailyScores as system context. Responses are personalized, not generic.

---

## Frontend Structure

### Next.js Web (Vercel)
```
app/
+-- (auth)/
|   +-- login/
|   +-- register/
|   +-- reset/
+-- (app)/                    -- protected, requires valid JWT
|   +-- dashboard/            -- BioIQ readiness score + metric cards
|   +-- metrics/              -- detailed health metric history + charts
|   +-- devices/              -- connect/disconnect integrations
|   +-- ai/                   -- BioIQ AI chat + insights
|   +-- providers/            -- manage healthcare provider access
|   +-- settings/             -- profile, account, notifications
+-- layout.tsx
```

### React Native / Expo (iPhone)
Feature-parallel with web at launch. Bottom tab navigation, native modals, Face ID for biometric re-auth. Calls the same Django API with the same JWT tokens.

### Design Language
- Aesthetic: Wix-inspired polish adapted for health. Bold, confident, approachable. Not clinical.
- Typography: Inter (web) / SF Pro (iOS). Large metric numbers dominate.
- Color: Deep navy/slate primary, electric blue or teal accent
- Animations: Framer Motion (web), React Native Animated (mobile). Score ring animates on load, cards stagger in.
- Data viz: Recharts with gradient fills. Curves, not spreadsheet charts.
- Dark mode: Supported from day one
- Onboarding: Guided step-by-step with Wix-style progress indicators

### Component Libraries
| Library | Purpose |
|---------|---------|
| shadcn/ui | Web UI primitives (fully customizable) |
| Framer Motion | Web animations |
| Recharts | Health data charts |
| TanStack Query | API state, caching, background refresh |
| React Native Paper | Mobile UI components |

---

## AWS Infrastructure (Free Tier)

| Service | Spec | Free Tier |
|---------|------|-----------|
| EC2 | t2.micro -- Django server | 750 hrs/month x 12 months |
| RDS | db.t3.micro PostgreSQL | 750 hrs/month x 12 months |
| S3 | File storage | 5GB + 20K requests/month |
| SES | Transactional email | 62,000 emails/month |
| ACM | SSL certificate | Free |
| Route 53 | DNS | ~$0.50/month |

Estimated cost after free tier: ~$30-40/month for minimal setup.
AWS BAA: Signed before any real PHI is stored (free, checkbox in AWS console).

---

## Project Workflow

See `issues.md` at project root for the issue to branch to test to PR workflow used throughout development.


---

## OWASP Top 10 (2025) Compliance

All BioIQ code must be designed and reviewed against the OWASP Top 10 2025 list. This applies to both Django backend and Next.js/React Native frontend.

| # | Risk | BioIQ Control |
|---|------|---------------|
| A01 | Broken Access Control | JWT auth on every endpoint; per-user data scoping in every query; ProviderAccess consent model; RBAC enforced in Django views |
| A02 | Cryptographic Failures | TLS 1.2+ in transit; AES-256 at rest (RDS + S3); field-level encryption for PHI; no secrets in source code (AWS Secrets Manager) |
| A03 | Injection | Django ORM exclusively (no raw SQL); DRF serializer validation on all inputs; parameterized queries only |
| A04 | Insecure Design | HIPAA-by-design data model; threat modeling before each sub-project; ProviderAccess explicit consent; audit logging built in, not bolted on |
| A05 | Security Misconfiguration | Django DEBUG=False in all non-local envs; security headers (HSTS, CSP, X-Frame-Options) enforced; no default credentials; automated config drift detection |
| A06 | Vulnerable and Outdated Components | Dependabot enabled on GitHub; pip-audit and npm audit in CI pipeline; weekly automated dependency scans |
| A07 | Identification and Authentication Failures | bcrypt password hashing; JWT short expiry (15 min); refresh token rotation; account lockout after failed attempts; MFA planned for future |
| A08 | Software and Data Integrity Failures | GitHub branch protection; signed commits enforced in CI; no unverified third-party packages without review |
| A09 | Security Logging and Monitoring Failures | AuditLog table for all PHI access; Django logging to CloudWatch; alerting on anomalous access patterns; log retention per HIPAA requirements |
| A10 | Server-Side Request Forgery (SSRF) | Allowlist for outbound HTTP calls (device OAuth endpoints only); no user-supplied URLs passed to backend HTTP clients |

OWASP compliance is verified at code review (PR checklist) and in periodic security scans. Each sub-project spec will include OWASP notes specific to its features.

---

## CI/CD Pipeline

**Platform:** GitHub Actions

### Pipeline Stages (runs on every PR and push to main)

```
PR opened / push to branch
        |
        v
+------------------+
|   LINT & FORMAT  |
|  Python: ruff    |
|  JS: ESLint      |
|  CSS: Stylelint  |
+--------+---------+
         |
         v
+------------------+
|   TYPE CHECK     |
|  Python: mypy    |
|  JS: tsc --noEmit|
+--------+---------+
         |
         v
+------------------+
|   SECURITY SCAN  |
|  Python: bandit  |
|  JS: npm audit   |
|  Deps: pip-audit |
+--------+---------+
         |
         v
+------------------+
|   TEST SUITE     |
|  Django: pytest  |
|  Next.js: Jest   |
|  Coverage >= 80% |
+--------+---------+
         |
         v
+------------------+
|   BUILD CHECK    |
|  next build      |
|  Django check    |
+--------+---------+
         |
    Pass? Yes
         |
         v
  PR ready to merge
```

### GitHub Branch Protection (main + staging)
- All pipeline stages must pass before merge
- At least 1 approving review required
- No direct pushes to main or staging
- Signed commits required

### Deployment Triggers
| Branch | Deploys To | Auto-deploy |
|--------|------------|-------------|
| feature/* | Local only | No |
| staging | Test environment | Yes, on merge |
| main | Production | Yes, on merge (with manual approval gate) |

### Code Quality Tools

| Tool | Language | Purpose |
|------|----------|---------|
| ruff | Python | Linting + formatting (replaces flake8, black, isort) |
| mypy | Python | Static type checking |
| bandit | Python | Security vulnerability scanning |
| pip-audit | Python | Dependency vulnerability scanning |
| pytest | Python | Test runner |
| pytest-cov | Python | Coverage reporting |
| ESLint | JS/TS | Linting |
| Prettier | JS/TS | Formatting |
| TypeScript | JS/TS | Type checking |
| Jest | JS/TS | Unit + integration tests |
| npm audit | JS/TS | Dependency vulnerability scanning |
| Dependabot | Both | Automated dependency update PRs |

---

## Environments

**Philosophy: develop like we are in prod.** Staging mirrors production exactly. No dev-only shortcuts in code. Feature flags are off by default. If it would not fly in prod, it does not land in staging.

### Three-Environment Model

| Environment | Purpose | Infrastructure | Data |
|-------------|---------|----------------|------|
| **Local (dev)** | Individual development | Docker Compose (Django + Postgres + Redis) | Synthetic seed data only. No real PHI ever in local. |
| **Staging (test)** | Integration testing, QA, pre-release validation | AWS (mirrors prod, smaller instance sizes) | Anonymized/synthetic data. HIPAA controls active. |
| **Production (prod)** | Live users | AWS (full spec) | Real user PHI. Full HIPAA controls. AWS BAA active. |

### Environment Configuration

Each environment uses its own:
- AWS account or isolated VPC
- RDS instance (no shared databases between envs)
- S3 bucket
- Django SECRET_KEY and database credentials (AWS Secrets Manager)
- Anthropic API key (separate keys per env for cost tracking)
- Vercel deployment (preview for staging, production for prod)

Environment variables are never committed to source control. `.env.example` documents required variables with placeholder values.

### Local Development Setup
- Docker Compose runs Django + PostgreSQL + Redis locally
- `.env.local` file (gitignored) holds local credentials
- `make seed` command populates synthetic health data for development
- Hot reload enabled for both Django and Next.js

### Staging Environment
- Deployed automatically on merge to `staging` branch
- Mirrors production infrastructure at reduced scale (t2.micro vs t3.small)
- Used for QA, integration testing with real device APIs (sandbox modes where available)
- All OWASP and HIPAA controls active -- not a relaxed environment

### Production Environment
- Deployed on merge to `main` with a manual approval gate in GitHub Actions
- Full AWS infrastructure per spec
- AWS BAA active
- CloudWatch monitoring + alerting
- Automated daily RDS snapshots (30-day retention)

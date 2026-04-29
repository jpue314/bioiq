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

## OWASP Top 10 Compliance (All Published Versions)

BioIQ is designed and reviewed against every published OWASP Top 10 list: 2017, 2021, and 2025. Controls that appear across multiple versions receive the strongest treatment. This applies to both Django backend and Next.js/React Native frontend.

OWASP compliance is verified at code review (PR checklist) and in periodic automated security scans. Each sub-project spec will include OWASP notes specific to its features.

---

### OWASP Top 10 — 2017

| # | Risk | BioIQ Control |
|---|------|---------------|
| A1:2017 | Injection | Django ORM exclusively; no raw SQL; DRF serializer validation on all inputs; parameterized queries only |
| A2:2017 | Broken Authentication | bcrypt hashing; JWT short expiry (15 min); refresh token rotation; account lockout after failed attempts |
| A3:2017 | Sensitive Data Exposure | TLS 1.2+ in transit; AES-256 at rest (RDS + S3); field-level PHI encryption; no PHI in logs |
| A4:2017 | XML External Entities (XXE) | No XML parsing in the stack; all APIs use JSON only; XXE vector eliminated by design |
| A5:2017 | Broken Access Control | Per-user data scoping on every query; JWT required on all protected endpoints; ProviderAccess explicit consent model |
| A6:2017 | Security Misconfiguration | DEBUG=False in all non-local envs; security headers enforced (HSTS, CSP, X-Frame-Options); no default credentials; config drift detection |
| A7:2017 | Cross-Site Scripting (XSS) | React/Next.js escapes output by default; Content-Security-Policy header; no dangerouslySetInnerHTML; DRF output serialized safely |
| A8:2017 | Insecure Deserialization | No pickle or unsafe deserialization; JSON only; DRF serializers validate all incoming data with explicit type checking |
| A9:2017 | Using Components with Known Vulnerabilities | Dependabot on GitHub; pip-audit and npm audit in CI; weekly automated scans; no unpinned dependencies in prod |
| A10:2017 | Insufficient Logging & Monitoring | AuditLog table for all PHI access; Django logging to CloudWatch; alerting on anomalous access patterns; HIPAA-compliant log retention |

---

### OWASP Top 10 — 2021

| # | Risk | Status vs 2017 | BioIQ Control |
|---|------|----------------|---------------|
| A01:2021 | Broken Access Control | Moved up from #5 | RBAC enforced in Django views; per-user queryset scoping; ProviderAccess revocation; account deletion cascade |
| A02:2021 | Cryptographic Failures | Renamed from Sensitive Data Exposure | TLS 1.2+; AES-256 at rest; field-level encryption (django-encrypted-fields); AWS Secrets Manager for credentials; no secrets in source |
| A03:2021 | Injection | Now includes XSS | Django ORM; DRF serializer validation; React auto-escaping; CSP header; no raw queries or eval() |
| A04:2021 | Insecure Design | New in 2021 | HIPAA-by-design data model; threat modeling before each sub-project; privacy-by-default; audit logging built in from day one |
| A05:2021 | Security Misconfiguration | Expanded | DEBUG=False; security headers; no default credentials; automated config checks in CI; environment parity (dev=prod) |
| A06:2021 | Vulnerable and Outdated Components | Renamed from A9:2017 | Dependabot; pip-audit + npm audit in CI; pinned dependencies; weekly scans |
| A07:2021 | Identification and Authentication Failures | Renamed from A2:2017 | bcrypt; JWT rotation; lockout policy; Sign in with Apple/Google; MFA planned |
| A08:2021 | Software and Data Integrity Failures | Expanded from A8:2017 | GitHub branch protection; signed commits in CI; verified third-party packages only; no CI/CD bypass |
| A09:2021 | Security Logging and Monitoring Failures | Renamed from A10:2017 | AuditLog for all PHI; CloudWatch alerts; anomaly detection; 6-year HIPAA log retention |
| A10:2021 | Server-Side Request Forgery (SSRF) | New in 2021 | Allowlist for all outbound HTTP (device OAuth endpoints only); no user-supplied URLs to backend HTTP clients |

---

### OWASP Top 10 — 2025

| # | Risk | Status vs 2021 | BioIQ Control |
|---|------|----------------|---------------|
| A01:2025 | Broken Access Control | Maintained from 2021 | All 2021 controls apply; additionally: automated access control tests in CI suite |
| A02:2025 | Cryptographic Failures | Maintained from 2021 | All 2021 controls apply; TLS 1.3 preferred; key rotation policy via AWS KMS |
| A03:2025 | Injection | Maintained from 2021 | All 2021 controls apply; AI prompt injection defense: user input sanitized before Claude API calls |
| A04:2025 | Insecure Design | Maintained from 2021 | All 2021 controls apply; OWASP review checklist on every PR |
| A05:2025 | Security Misconfiguration | Maintained from 2021 | All 2021 controls apply; infrastructure-as-code (no manual console changes in prod) |
| A06:2025 | Vulnerable and Outdated Components | Maintained from 2021 | All 2021 controls apply; automated PR creation by Dependabot within 48hrs of CVE |
| A07:2025 | Identification and Authentication Failures | Maintained from 2021 | All 2021 controls apply; passkeys/Face ID in roadmap |
| A08:2025 | Software and Data Integrity Failures | Maintained from 2021 | All 2021 controls apply; SBOM (Software Bill of Materials) generated in CI |
| A09:2025 | Security Logging and Monitoring Failures | Maintained from 2021 | All 2021 controls apply; real-time alerting on failed auth spikes and unusual PHI access |
| A10:2025 | Server-Side Request Forgery (SSRF) | Maintained from 2021 | All 2021 controls apply; outbound request auditing in CloudWatch |

---

### Cross-Version Coverage Summary

Controls that appeared in 2017, were reinforced in 2021, and maintained in 2025 receive the highest implementation priority:
- Injection defense (A1:2017 -> A03:2021 -> A03:2025)
- Broken Access Control (A5:2017 -> A01:2021 -> A01:2025)
- Cryptographic Failures (A3:2017 -> A02:2021 -> A02:2025)
- Logging & Monitoring (A10:2017 -> A09:2021 -> A09:2025)

New risks introduced in 2021 and 2025 (Insecure Design, SSRF, Software Integrity) are addressed from the start rather than retrofitted.

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


# BioIQ Tech Stack Reference

> Personal reference — what we're using, what it does, and why we chose it.

---

## Backend

### Django 5.2
Python's "batteries-included" web framework. Gives us the ORM, admin panel, migrations, and auth system out of the box. We're running it as a REST API server (no Django templates rendered).

### Django REST Framework (DRF) 3.15
Adds serializers, ViewSets, authentication classes, and browsable API on top of Django. Our views all inherit from DRF's `APIView` or generic views.

### SimpleJWT 5.3
JWT token library for DRF. Issues short-lived **access tokens** (15 min) returned in the response body, and long-lived **refresh tokens** (30 days) stored in an HttpOnly cookie — the cookie pattern is more XSS-resistant than localStorage.

Token blacklisting is enabled: when a user logs out, the refresh token's JTI is stored in the DB so it can't be reused even before expiry.

### django-allauth 0.63
Handles social OAuth (Google, Apple sign-in) and email verification flows. We configure email as the primary identifier — no username field on our `User` model.

### django-encrypted-fields 1.1.2
Transparently encrypts sensitive model fields at the Django ORM layer before they hit the database. Used for OAuth tokens on `ConnectedDevice` (wearable API credentials). Requires `FIELD_ENCRYPTION_KEY` in env.

### PostgreSQL (AWS RDS in production)
Primary database. We use SQLite for local development/testing to skip the Docker dependency.

### psycopg2-binary
PostgreSQL adapter for Python. The `-binary` variant bundles the C library — easier to install, slightly larger, perfectly fine for our use case.

### python-decouple 3.8
Reads config from `.env` files and environment variables. All secrets (`SECRET_KEY`, `DB_PASSWORD`, `FIELD_ENCRYPTION_KEY`, etc.) are injected through decouple — nothing hardcoded.

### django-cors-headers 4.3
Adds CORS response headers so the Next.js frontend (running on a different origin) can call the API. Configured per environment: loose in local, strict in staging/production.

### Anthropic SDK 0.28
Official Python client for the Claude API. Used in `apps/ai/services.py` to route health data questions to Claude. We'll add prompt caching to reduce latency and cost on repeated context.

### boto3 1.34
AWS SDK for Python. Used for S3 (file uploads) and SES (transactional email).

---

## Testing

### pytest + pytest-django
pytest is our test runner. pytest-django integrates it with Django — it handles test database creation/teardown and provides the `@pytest.mark.django_db` marker. Test settings point to SQLite locally.

### factory-boy
Generates realistic model instances for tests. Each app has a `tests/factories.py`. Factories use `factory.Sequence` for unique fields and `factory.SubFactory` for FK relationships.

### pytest-cov
Measures test coverage. Configured to fail if total coverage drops below 80% (`--cov-fail-under=80` in `pytest.ini`).

---

## Code Quality

### Ruff 0.4
Extremely fast Python linter + formatter (written in Rust). Replaces flake8, isort, and pyupgrade in one tool. Configured in `ruff.toml`: line length 88, standard rule sets E/F/I/N/W/UP.

### mypy + django-stubs
Static type checker for Python. `django-stubs` adds Django-specific type information (model fields, querysets, etc.). Migrations are excluded from type checking.

### bandit
Security-focused linter — catches common Python security issues (hardcoded secrets, use of `eval`, insecure hash functions, etc.).

### pip-audit
Scans installed dependencies for known CVEs. Run in CI to catch vulnerable transitive dependencies.

---

## Frontend

### Next.js 14 (App Router)
React framework with server-side rendering and file-based routing. We use the App Router (`src/app/`) — layouts, loading states, and error boundaries are all built-in. Next.js is a **thin display client only** — no PHI is stored or processed on Vercel servers.

### shadcn/ui
Component library built on Radix UI primitives + Tailwind CSS. Components are copied into the repo (not installed as a package) so we own the source and can customise freely.

### TanStack Query (React Query) v5
Async state management for API calls. Handles caching, background refetching, optimistic updates, and loading/error states. Replaces manual `useEffect` + `useState` fetch patterns.

### Framer Motion
Animation library for React. Used for page transitions and micro-interactions (score cards, loading states).

### Axios
HTTP client. We have a single Axios instance (`src/lib/api.ts`) that injects the JWT access token, handles 401 responses by attempting a token refresh, and retries the original request.

---

## Infrastructure

### AWS EC2
The Django API server runs here, inside the AWS HIPAA boundary. All PHI stays on EC2 + RDS — it never leaves the AWS environment.

### AWS RDS (PostgreSQL)
Managed PostgreSQL. Automatic backups, encryption at rest, Multi-AZ failover in production.

### AWS S3
File storage — profile images, exported health reports.

### AWS SES
Transactional email — email verification, password resets, provider access notifications.

### Vercel
Hosts the Next.js frontend. Stateless — only serves the React app and proxies API requests to EC2. No PHI stored here.

### Docker + Docker Compose
Local development environment. `docker-compose.yml` runs PostgreSQL and the Django dev server in containers so the setup is reproducible.

### GitHub Actions
CI/CD pipeline:
- `ci.yml`: runs on every PR — ruff, mypy, bandit, pip-audit, pytest with coverage
- `deploy.yml`: runs on merge to `main` — deploys backend to EC2, frontend to Vercel

---

## Security Highlights

| Concern | Solution |
|---|---|
| PHI data at rest | `django-encrypted-fields` encrypts sensitive columns |
| PHI access auditing | `AuditLog` model + `AuditMixin` on every PHI-touching view |
| Token theft via XSS | Refresh token in HttpOnly cookie (JS-inaccessible) |
| Token reuse after logout | SimpleJWT token blacklist |
| Secrets in code | python-decouple + environment variables only |
| Provider access delegation | `ProviderAccess` model with expiry + revocation |

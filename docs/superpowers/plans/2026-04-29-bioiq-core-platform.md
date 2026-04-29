# BioIQ Core Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the BioIQ Core Platform: a HIPAA-compliant health data hub with a Django REST API, Next.js web frontend, JWT + social auth, Claude AI integration, and GitHub Actions CI/CD deployed on AWS (backend) and Vercel (frontend).

**Architecture:** Django monolith on AWS EC2 serves a REST API consumed by a Next.js web app on Vercel. All PHI lives within the AWS HIPAA boundary. Next.js is a thin display client only.

**Tech Stack:** Django 5.x + DRF + SimpleJWT + django-allauth | PostgreSQL (AWS RDS) | Anthropic Claude API | Next.js 14 (App Router) + shadcn/ui + TanStack Query + Framer Motion | GitHub Actions | AWS EC2 + RDS + S3 + SES | Vercel

---

## File Structure

```
bioiq/
+-- backend/
|   +-- manage.py
|   +-- requirements.txt
|   +-- requirements-dev.txt
|   +-- Dockerfile
|   +-- .env.example
|   +-- pytest.ini
|   +-- mypy.ini
|   +-- ruff.toml
|   +-- bioiq/
|   |   +-- settings/
|   |   |   +-- base.py
|   |   |   +-- local.py
|   |   |   +-- staging.py
|   |   |   +-- production.py
|   |   +-- urls.py
|   |   +-- wsgi.py
|   |   +-- asgi.py
|   +-- apps/
|   |   +-- users/
|   |   |   +-- models.py        # User, HealthProfile
|   |   |   +-- serializers.py
|   |   |   +-- views.py
|   |   |   +-- urls.py
|   |   |   +-- admin.py
|   |   |   +-- tests/
|   |   |       +-- factories.py
|   |   |       +-- test_models.py
|   |   |       +-- test_views.py
|   |   +-- health/
|   |   |   +-- models.py        # DailyScore, HealthMetric
|   |   |   +-- serializers.py
|   |   |   +-- views.py
|   |   |   +-- urls.py
|   |   |   +-- tests/
|   |   |       +-- factories.py
|   |   |       +-- test_models.py
|   |   |       +-- test_views.py
|   |   +-- devices/
|   |   |   +-- models.py        # ConnectedDevice
|   |   |   +-- serializers.py
|   |   |   +-- views.py
|   |   |   +-- urls.py
|   |   |   +-- tests/
|   |   |       +-- factories.py
|   |   |       +-- test_views.py
|   |   +-- providers/
|   |   |   +-- models.py        # ProviderAccess
|   |   |   +-- serializers.py
|   |   |   +-- views.py
|   |   |   +-- urls.py
|   |   |   +-- tests/
|   |   |       +-- factories.py
|   |   |       +-- test_views.py
|   |   +-- ai/
|   |   |   +-- models.py        # AIConversation
|   |   |   +-- serializers.py
|   |   |   +-- views.py
|   |   |   +-- urls.py
|   |   |   +-- services.py      # Claude API routing
|   |   |   +-- tests/
|   |   |       +-- test_services.py
|   |   |       +-- test_views.py
|   |   +-- audit/
|   |       +-- models.py        # AuditLog
|   |       +-- mixins.py        # AuditMixin for views
|   |       +-- tests/
|   |           +-- test_models.py
|   +-- conftest.py
+-- frontend/
|   +-- package.json
|   +-- tsconfig.json
|   +-- next.config.ts
|   +-- .env.example
|   +-- src/
|   |   +-- app/
|   |   |   +-- (auth)/
|   |   |   |   +-- login/page.tsx
|   |   |   |   +-- register/page.tsx
|   |   |   |   +-- reset/page.tsx
|   |   |   +-- (app)/
|   |   |   |   +-- dashboard/page.tsx
|   |   |   |   +-- metrics/page.tsx
|   |   |   |   +-- devices/page.tsx
|   |   |   |   +-- ai/page.tsx
|   |   |   |   +-- providers/page.tsx
|   |   |   |   +-- settings/page.tsx
|   |   |   +-- layout.tsx
|   |   |   +-- globals.css
|   |   +-- components/
|   |   |   +-- ui/              # shadcn/ui primitives
|   |   |   +-- auth/
|   |   |   |   +-- LoginForm.tsx
|   |   |   |   +-- RegisterForm.tsx
|   |   |   +-- dashboard/
|   |   |   |   +-- ReadinessScore.tsx
|   |   |   |   +-- MetricCard.tsx
|   |   |   +-- layout/
|   |   |       +-- AppShell.tsx
|   |   |       +-- NavBar.tsx
|   |   +-- lib/
|   |   |   +-- api.ts           # Axios instance + interceptors
|   |   |   +-- auth.ts          # Auth context + hooks
|   |   |   +-- utils.ts         # cn() and shared helpers
|   |   +-- types/
|   |       +-- index.ts         # Shared TypeScript interfaces
|   +-- __tests__/
+-- docker-compose.yml
+-- .gitignore
+-- .github/
|   +-- workflows/
|       +-- ci.yml
|       +-- deploy.yml
+-- issues.md
+-- docs/

---

## Task 1: Monorepo Structure, Docker Compose, and Tooling Config

**Files:**
- Create: `docker-compose.yml`
- Create: `backend/Dockerfile`
- Create: `backend/.env.example`
- Create: `backend/requirements.txt`
- Create: `backend/requirements-dev.txt`
- Create: `backend/ruff.toml`
- Create: `backend/pytest.ini`
- Create: `backend/mypy.ini`
- Create: `.gitignore`

- [ ] **Step 1: Create project root structure**

```bash
mkdir -p backend frontend .github/workflows
```

`.gitignore`:
```
__pycache__/
*.py[cod]
.venv/
venv/
.env
.env.local
*.log
db.sqlite3
media/
node_modules/
.next/
out/
*.tsbuildinfo
.DS_Store
Thumbs.db
.vscode/
.idea/
.coverage
htmlcov/
.pytest_cache/
```

- [ ] **Step 2: Write backend/requirements.txt**

```
Django==5.2
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.1
django-allauth==0.63.3
django-encrypted-fields==0.2.0
psycopg2-binary==2.9.9
boto3==1.34.0
anthropic==0.28.0
python-decouple==3.8
django-cors-headers==4.3.1
```

- [ ] **Step 3: Write backend/requirements-dev.txt**

```
-r requirements.txt
pytest==8.2.0
pytest-django==4.8.0
pytest-cov==5.0.0
factory-boy==3.3.0
ruff==0.4.4
mypy==1.10.0
django-stubs==5.0.2
bandit==1.7.8
pip-audit==2.7.3
```

- [ ] **Step 4: Write backend/ruff.toml**

```toml
line-length = 88
target-version = "py312"

[lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]

[lint.isort]
known-first-party = ["apps", "bioiq"]
```

- [ ] **Step 5: Write backend/pytest.ini**

```ini
[pytest]
DJANGO_SETTINGS_MODULE = bioiq.settings.local
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov=apps --cov-report=term-missing --cov-fail-under=80
```

- [ ] **Step 6: Write backend/mypy.ini**

```ini
[mypy]
plugins = mypy_django_plugin.main
django_settings_module = bioiq.settings.local
ignore_missing_imports = True

[mypy.plugins.django-stubs]
django_settings_module = "bioiq.settings.local"

[mypy-*.migrations.*]
ignore_errors = True
```

- [ ] **Step 7: Write backend/Dockerfile**

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

- [ ] **Step 8: Write docker-compose.yml**

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: bioiq
      POSTGRES_PASSWORD: bioiq
      POSTGRES_DB: bioiq_local
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    depends_on:
      - db

  frontend:
    image: node:20-alpine
    working_dir: /app
    command: npm run dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    env_file:
      - ./frontend/.env.local

volumes:
  postgres_data:
```

- [ ] **Step 9: Write backend/.env.example**

```
SECRET_KEY=replace-with-50-char-random-string
DEBUG=True
DJANGO_SETTINGS_MODULE=bioiq.settings.local
DB_NAME=bioiq_local
DB_USER=bioiq
DB_PASSWORD=bioiq
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_SES_REGION_NAME=us-east-1
ANTHROPIC_API_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
APPLE_CLIENT_ID=
APPLE_PRIVATE_KEY=
FIELD_ENCRYPTION_KEY=
```

- [ ] **Step 10: Commit**

```bash
git add .
git commit -m "feat: add monorepo structure, Docker Compose, and tooling config"
```

---

## Task 2: Django Project Bootstrap and Multi-Environment Settings

**Files:**
- Create: `backend/bioiq/settings/base.py`
- Create: `backend/bioiq/settings/local.py`
- Create: `backend/bioiq/settings/staging.py`
- Create: `backend/bioiq/settings/production.py`
- Create: `backend/bioiq/urls.py`
- Create: `backend/conftest.py`

- [ ] **Step 1: Bootstrap and restructure settings**

```bash
cd backend
pip install -r requirements-dev.txt
django-admin startproject bioiq .
mkdir -p bioiq/settings
touch bioiq/settings/__init__.py
```

Delete the generated `bioiq/settings.py` file -- it will be replaced by the settings package.

- [ ] **Step 2: Write bioiq/settings/base.py**

```python
from pathlib import Path
from datetime import timedelta
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",")

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.apple",
]

LOCAL_APPS = [
    "apps.users",
    "apps.health",
    "apps.devices",
    "apps.providers",
    "apps.ai",
    "apps.audit",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "bioiq.urls"
AUTH_USER_MODEL = "users.User"
SITE_ID = 1

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "bioiq.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="bioiq_local"),
        "USER": config("DB_USER", default="bioiq"),
        "PASSWORD": config("DB_PASSWORD", default="bioiq"),
        "HOST": config("DB_HOST", default="db"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
}

CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="http://localhost:3000").split(",")
CORS_ALLOW_CREDENTIALS = True

FIELD_ENCRYPTION_KEY = config("FIELD_ENCRYPTION_KEY", default="")
ANTHROPIC_API_KEY = config("ANTHROPIC_API_KEY", default="")
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="")
AWS_SES_REGION_NAME = config("AWS_SES_REGION_NAME", default="us-east-1")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
```

- [ ] **Step 3: Write bioiq/settings/local.py**

```python
from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
```

- [ ] **Step 4: Write bioiq/settings/staging.py**

```python
from .base import *  # noqa: F401, F403

DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
```

- [ ] **Step 5: Write bioiq/settings/production.py**

```python
from .base import *  # noqa: F401, F403

DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
```

- [ ] **Step 6: Write bioiq/urls.py**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls")),
    path("api/", include("apps.health.urls")),
    path("api/", include("apps.devices.urls")),
    path("api/", include("apps.providers.urls")),
    path("api/ai/", include("apps.ai.urls")),
]
```

- [ ] **Step 7: Write backend/conftest.py**

```python
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    from apps.users.tests.factories import UserFactory
    return UserFactory()


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client
```

- [ ] **Step 8: Create all app directories**

```bash
cd backend
mkdir -p apps/users/tests apps/health/tests apps/devices/tests
mkdir -p apps/providers/tests apps/ai/tests apps/audit/tests
touch apps/__init__.py
for app in users health devices providers ai audit; do
    touch apps/$app/__init__.py apps/$app/tests/__init__.py
    touch apps/$app/models.py apps/$app/serializers.py
    touch apps/$app/views.py apps/$app/urls.py apps/$app/admin.py
done
```

- [ ] **Step 9: Verify Django loads correctly**

```bash
cd backend
cp .env.example .env
python manage.py check
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 10: Commit**

```bash
git add backend/
git commit -m "feat: Django project bootstrap with multi-environment settings"
```

---

## Task 3: Custom User and HealthProfile Models (TDD)

**Files:**
- Create: `backend/apps/users/models.py`
- Create: `backend/apps/users/tests/factories.py`
- Create: `backend/apps/users/tests/test_models.py`
- Create: `backend/apps/users/admin.py`

- [ ] **Step 1: Write failing tests for User model**

`backend/apps/users/tests/test_models.py`:
```python
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_user_created_with_email_as_identifier():
    user = User.objects.create_user(
        email="test@example.com",
        password="SecurePass123!",
        first_name="Jane",
        last_name="Doe",
    )
    assert user.email == "test@example.com"
    assert user.username is None
    assert user.check_password("SecurePass123!")
    assert not user.is_verified


@pytest.mark.django_db
def test_user_email_must_be_unique():
    User.objects.create_user(email="dup@example.com", password="Pass123456!")
    with pytest.raises(Exception):
        User.objects.create_user(email="dup@example.com", password="Pass123456!")


@pytest.mark.django_db
def test_health_profile_created_for_user():
    from apps.users.models import HealthProfile
    user = User.objects.create_user(email="hp@example.com", password="Pass123456!")
    profile = HealthProfile.objects.create(
        user=user,
        date_of_birth="1990-01-01",
        biological_sex="M",
        height_cm=180,
        weight_kg=80.0,
    )
    assert profile.user == user
    assert profile.height_cm == 180
```

- [ ] **Step 2: Run tests -- expect failure**

```bash
cd backend
pytest apps/users/tests/test_models.py -v
```

Expected: `FAILED -- apps.users.models does not exist`

- [ ] **Step 3: Implement User and HealthProfile models**

`backend/apps/users/models.py`:
```python
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str, **extra_fields) -> "User":
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        return self.email


class HealthProfile(models.Model):
    class Sex(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"
        PREFER_NOT = "N", "Prefer not to say"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="health_profile")
    date_of_birth = models.DateField(null=True, blank=True)
    biological_sex = models.CharField(max_length=1, choices=Sex.choices, blank=True)
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    fitness_goals = models.JSONField(default=list, blank=True)
    medical_conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_profiles"

    def __str__(self) -> str:
        return f"HealthProfile({self.user.email})"
```

- [ ] **Step 4: Create and run migrations**

```bash
cd backend
python manage.py makemigrations users
python manage.py migrate
```

Expected: `OK` for all migrations.

- [ ] **Step 5: Write test factory**

`backend/apps/users/tests/factories.py`:
```python
import factory
from factory.django import DjangoModelFactory
from apps.users.models import User, HealthProfile


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_verified = True
    password = factory.PostGenerationMethodCall("set_password", "TestPassword123!")


class HealthProfileFactory(DjangoModelFactory):
    class Meta:
        model = HealthProfile

    user = factory.SubFactory(UserFactory)
    date_of_birth = "1990-06-15"
    biological_sex = HealthProfile.Sex.MALE
    height_cm = 178
    weight_kg = "75.5"
    fitness_goals = ["build endurance", "lose weight"]
```

- [ ] **Step 6: Run tests -- expect pass**

```bash
cd backend
pytest apps/users/tests/test_models.py -v
```

Expected: `3 passed`

- [ ] **Step 7: Write admin registration**

`backend/apps/users/admin.py`:
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, HealthProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "first_name", "last_name", "is_verified", "is_staff")
    list_filter = ("is_staff", "is_verified", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "is_verified")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    filter_horizontal = ()


@admin.register(HealthProfile)
class HealthProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "biological_sex", "height_cm", "weight_kg")
    raw_id_fields = ("user",)
```

- [ ] **Step 8: Commit**

```bash
git add backend/apps/users/ backend/apps/users/migrations/
git commit -m "feat: add custom User and HealthProfile models with TDD"
```

---

## Task 4: AuditLog Model and View Mixin (TDD)

**Files:**
- Create: `backend/apps/audit/models.py`
- Create: `backend/apps/audit/mixins.py`
- Create: `backend/apps/audit/tests/test_models.py`

- [ ] **Step 1: Write failing test for AuditLog**

`backend/apps/audit/tests/test_models.py`:
```python
import pytest
from apps.audit.models import AuditLog


@pytest.mark.django_db
def test_audit_log_records_phi_access(user):
    log = AuditLog.objects.create(
        user=user,
        actor=user,
        action=AuditLog.Action.READ,
        resource_type="HealthProfile",
        resource_id=str(user.pk),
        ip_address="127.0.0.1",
        user_agent="pytest",
    )
    assert log.pk is not None
    assert log.action == AuditLog.Action.READ
    assert log.user == user


@pytest.mark.django_db
def test_audit_log_str(user):
    log = AuditLog.objects.create(
        user=user,
        actor=user,
        action=AuditLog.Action.WRITE,
        resource_type="DailyScore",
        resource_id="1",
        ip_address="127.0.0.1",
        user_agent="test",
    )
    assert "DailyScore" in str(log)
```

- [ ] **Step 2: Run tests -- expect failure**

```bash
pytest apps/audit/tests/test_models.py -v
```

Expected: `ImportError: cannot import name AuditLog`

- [ ] **Step 3: Implement AuditLog model**

`backend/apps/audit/models.py`:
```python
from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    class Action(models.TextChoices):
        READ = "read", "Read"
        WRITE = "write", "Write"
        DELETE = "delete", "Delete"
        SHARE = "share", "Share"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs_as_subject",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs_as_actor",
    )
    action = models.CharField(max_length=10, choices=Action.choices)
    resource_type = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["resource_type", "resource_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.resource_type}/{self.resource_id} by {self.actor}"
```

- [ ] **Step 4: Implement AuditMixin for views**

`backend/apps/audit/mixins.py`:
```python
from .models import AuditLog


class AuditMixin:
    audit_resource_type: str = ""

    def _log(self, request, action: str, resource_id: str) -> None:
        if not request.user.is_authenticated:
            return
        AuditLog.objects.create(
            user=request.user,
            actor=request.user,
            action=action,
            resource_type=self.audit_resource_type,
            resource_id=resource_id,
            ip_address=request.META.get("REMOTE_ADDR", "0.0.0.0"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

    def log_read(self, request, resource_id: str) -> None:
        self._log(request, AuditLog.Action.READ, resource_id)

    def log_write(self, request, resource_id: str) -> None:
        self._log(request, AuditLog.Action.WRITE, resource_id)

    def log_delete(self, request, resource_id: str) -> None:
        self._log(request, AuditLog.Action.DELETE, resource_id)
```

- [ ] **Step 5: Run migrations and tests**

```bash
python manage.py makemigrations audit
python manage.py migrate
pytest apps/audit/tests/test_models.py -v
```

Expected: `2 passed`

- [ ] **Step 6: Commit**

```bash
git add apps/audit/
git commit -m "feat: add AuditLog model and AuditMixin for HIPAA compliance"
```

---

## Task 5: Health, Device, Provider, and AI Models (TDD)

**Files:**
- Create: `backend/apps/health/models.py`
- Create: `backend/apps/devices/models.py`
- Create: `backend/apps/providers/models.py`
- Create: `backend/apps/ai/models.py`
- Create: `backend/apps/health/tests/test_models.py`

- [ ] **Step 1: Write failing tests**

`backend/apps/health/tests/test_models.py`:
```python
import pytest
from apps.health.models import DailyScore, HealthMetric


@pytest.mark.django_db
def test_daily_score_created_for_user(user):
    score = DailyScore.objects.create(
        user=user,
        date="2026-04-29",
        readiness_score=82,
        sleep_score=78,
        recovery_score=85,
        activity_score=80,
        score_breakdown={"hrv": 65, "resting_hr": 52},
    )
    assert score.readiness_score == 82
    assert score.score_breakdown["hrv"] == 65


@pytest.mark.django_db
def test_health_metric_stores_raw_value(user):
    metric = HealthMetric.objects.create(
        user=user,
        source=None,
        metric_type=HealthMetric.MetricType.HRV,
        value=65.0,
        unit="ms",
        recorded_at="2026-04-29T06:00:00Z",
    )
    assert metric.metric_type == HealthMetric.MetricType.HRV
    assert metric.value == 65.0
```

- [ ] **Step 2: Run tests -- expect failure**

```bash
pytest apps/health/tests/test_models.py -v
```

Expected: `ImportError: cannot import name DailyScore`

- [ ] **Step 3: Implement health/models.py**

```python
from django.conf import settings
from django.db import models


class DailyScore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="daily_scores")
    date = models.DateField()
    readiness_score = models.PositiveSmallIntegerField()
    sleep_score = models.PositiveSmallIntegerField(null=True, blank=True)
    recovery_score = models.PositiveSmallIntegerField(null=True, blank=True)
    activity_score = models.PositiveSmallIntegerField(null=True, blank=True)
    score_breakdown = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "daily_scores"
        unique_together = [("user", "date")]
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.user.email} - {self.date} - {self.readiness_score}"


class HealthMetric(models.Model):
    class MetricType(models.TextChoices):
        HRV = "hrv", "HRV"
        RESTING_HR = "resting_hr", "Resting Heart Rate"
        STEPS = "steps", "Steps"
        SLEEP_DURATION = "sleep_duration", "Sleep Duration"
        SLEEP_QUALITY = "sleep_quality", "Sleep Quality"
        CALORIES = "calories", "Calories Burned"
        OXYGEN_SAT = "spo2", "Blood Oxygen Saturation"
        STRESS = "stress", "Stress Score"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="health_metrics")
    source = models.ForeignKey("devices.ConnectedDevice", on_delete=models.SET_NULL, null=True, blank=True)
    metric_type = models.CharField(max_length=30, choices=MetricType.choices)
    value = models.FloatField()
    unit = models.CharField(max_length=20)
    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "health_metrics"
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["user", "metric_type", "recorded_at"]),
        ]
```

- [ ] **Step 4: Implement devices/models.py**

```python
from django.conf import settings
from django.db import models


class ConnectedDevice(models.Model):
    class Provider(models.TextChoices):
        WHOOP = "whoop", "Whoop"
        APPLE_HEALTH = "apple_health", "Apple Health"
        GARMIN = "garmin", "Garmin"
        FITBIT = "fitbit", "Fitbit"
        STRAVA = "strava", "Strava"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="devices")
    provider = models.CharField(max_length=20, choices=Provider.choices)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "connected_devices"
        unique_together = [("user", "provider")]
```

- [ ] **Step 5: Implement providers/models.py**

```python
from django.conf import settings
from django.db import models


class ProviderAccess(models.Model):
    class AccessLevel(models.TextChoices):
        SUMMARY = "read_summary", "Read Summary"
        FULL = "read_full", "Read Full"
        METRICS = "read_metrics", "Read Metrics"

    class ProviderType(models.TextChoices):
        PHYSICIAN = "physician", "Physician"
        COACH = "coach", "Health Coach"
        SPECIALIST = "specialist", "Specialist"
        OTHER = "other", "Other"

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="provider_accesses")
    provider_name = models.CharField(max_length=200)
    provider_email = models.EmailField()
    provider_type = models.CharField(max_length=20, choices=ProviderType.choices, default=ProviderType.OTHER)
    access_level = models.CharField(max_length=20, choices=AccessLevel.choices, default=AccessLevel.SUMMARY)
    authorized_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "provider_accesses"

    @property
    def is_active(self) -> bool:
        from django.utils import timezone
        if self.revoked_at:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True
```

- [ ] **Step 6: Implement ai/models.py**

```python
from django.conf import settings
from django.db import models


class AIConversation(models.Model):
    class ConversationType(models.TextChoices):
        CHAT = "chat", "General Chat"
        INSIGHTS = "insights", "Health Insights"
        QUESTIONS = "questions", "Appointment Questions"
        WORKOUT = "workout", "Workout Plan"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_conversations")
    messages = models.JSONField(default=list)
    conversation_type = models.CharField(max_length=20, choices=ConversationType.choices, default=ConversationType.CHAT)
    model_used = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_conversations"
        ordering = ["-updated_at"]
```

- [ ] **Step 7: Run migrations and all tests so far**

```bash
python manage.py makemigrations health devices providers ai
python manage.py migrate
pytest apps/health/tests/test_models.py apps/audit/tests/ apps/users/tests/test_models.py -v
```

Expected: `7 passed`

- [ ] **Step 8: Commit**

```bash
git add apps/health/ apps/devices/ apps/providers/ apps/ai/
git commit -m "feat: add DailyScore, HealthMetric, ConnectedDevice, ProviderAccess, AIConversation models"
```

---

## Task 6: JWT Authentication API (TDD)

**Files:**
- Create: `backend/apps/users/views.py`
- Create: `backend/apps/users/serializers.py`
- Create: `backend/apps/users/urls.py`
- Create: `backend/apps/users/tests/test_views.py`

- [ ] **Step 1: Write failing auth endpoint tests**

`backend/apps/users/tests/test_views.py`:
```python
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_register_creates_user_and_returns_tokens(api_client):
    url = reverse("auth-register")
    response = api_client.post(url, {
        "email": "new@example.com",
        "password": "StrongPass123!",
        "first_name": "Jane",
        "last_name": "Doe",
    }, format="json")
    assert response.status_code == 201
    assert "access" in response.data
    assert response.cookies.get("refresh_token") is not None


@pytest.mark.django_db
def test_login_returns_access_token_and_sets_cookie(api_client, user):
    url = reverse("auth-login")
    response = api_client.post(url, {
        "email": user.email,
        "password": "TestPassword123!",
    }, format="json")
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" not in response.data
    assert response.cookies.get("refresh_token") is not None


@pytest.mark.django_db
def test_logout_clears_refresh_cookie(auth_client):
    url = reverse("auth-logout")
    response = auth_client.post(url)
    assert response.status_code == 200
    assert response.cookies["refresh_token"].value == ""


@pytest.mark.django_db
def test_unauthenticated_request_returns_401(api_client):
    url = reverse("user-me")
    response = api_client.get(url)
    assert response.status_code == 401
```

- [ ] **Step 2: Run tests -- expect failure**

```bash
pytest apps/users/tests/test_views.py -v
```

Expected: `NoReverseMatch: Reverse for auth-register not found`

- [ ] **Step 3: Write serializers**

`backend/apps/users/serializers.py`:
```python
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import HealthProfile

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=12, write_only=True)
    first_name = serializers.CharField(max_length=150, default="")
    last_name = serializers.CharField(max_length=150, default="")

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data: dict) -> dict:
        user = User.objects.create_user(**validated_data)
        HealthProfile.objects.create(user=user)
        refresh = RefreshToken.for_user(user)
        return {"user": user, "access": str(refresh.access_token), "refresh": str(refresh)}


class HealthProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProfile
        fields = ["date_of_birth", "biological_sex", "height_cm", "weight_kg", "fitness_goals", "medical_conditions"]


class UserSerializer(serializers.ModelSerializer):
    health_profile = HealthProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "is_verified", "created_at", "health_profile"]
        read_only_fields = ["id", "email", "is_verified", "created_at"]
```

- [ ] **Step 4: Write auth views**

`backend/apps/users/views.py`:
```python
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()

REFRESH_COOKIE = "refresh_token"
COOKIE_MAX_AGE = 30 * 24 * 60 * 60


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        REFRESH_COOKIE,
        token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        secure=True,
        samesite="Lax",
    )


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        response = Response({"access": result["access"]}, status=status.HTTP_201_CREATED)
        _set_refresh_cookie(response, result["refresh"])
        return response


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        email = request.data.get("email", "")
        password = request.data.get("password", "")
        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        response = Response({"access": str(refresh.access_token)})
        _set_refresh_cookie(response, str(refresh))
        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        token = request.COOKIES.get(REFRESH_COOKIE)
        if token:
            try:
                RefreshToken(token).blacklist()
            except TokenError:
                pass
        response = Response({"detail": "Logged out."})
        response.delete_cookie(REFRESH_COOKIE)
        return response


class TokenRefreshCookieView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        token = request.COOKIES.get(REFRESH_COOKIE)
        if not token:
            return Response({"detail": "No refresh token."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            refresh = RefreshToken(token)
            access = str(refresh.access_token)
            response = Response({"access": access})
            _set_refresh_cookie(response, str(refresh))
            return response
        except TokenError:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_401_UNAUTHORIZED)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        return Response(UserSerializer(request.user).data)

    def patch(self, request: Request) -> Response:
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request: Request) -> Response:
        request.user.delete()
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(REFRESH_COOKIE)
        return response
```

- [ ] **Step 5: Write URL config**

`backend/apps/users/urls.py`:
```python
from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="auth-register"),
    path("login/", views.LoginView.as_view(), name="auth-login"),
    path("logout/", views.LogoutView.as_view(), name="auth-logout"),
    path("token/refresh/", views.TokenRefreshCookieView.as_view(), name="auth-token-refresh"),
    path("me/", views.MeView.as_view(), name="user-me"),
]
```

- [ ] **Step 6: Run tests -- expect pass**

```bash
pytest apps/users/tests/test_views.py -v
```

Expected: `4 passed`

- [ ] **Step 7: Commit**

```bash
git add apps/users/
git commit -m "feat: JWT auth API -- register, login, logout, refresh, profile"
```

---

## Task 7: Dashboard Scores API (TDD)

**Files:**
- Create: `backend/apps/health/serializers.py`
- Create: `backend/apps/health/views.py`
- Create: `backend/apps/health/urls.py`
- Create: `backend/apps/health/tests/factories.py`
- Create: `backend/apps/health/tests/test_views.py`

- [ ] **Step 1: Write failing tests**

`backend/apps/health/tests/test_views.py`:
```python
import pytest
from django.urls import reverse
from django.utils import timezone
from apps.health.tests.factories import DailyScoreFactory


@pytest.mark.django_db
def test_today_score_returns_readiness(auth_client, user):
    DailyScoreFactory(user=user, date=timezone.now().date(), readiness_score=77)
    response = auth_client.get(reverse("scores-today"))
    assert response.status_code == 200
    assert response.data["readiness_score"] == 77


@pytest.mark.django_db
def test_today_score_returns_404_when_no_score_exists(auth_client):
    response = auth_client.get(reverse("scores-today"))
    assert response.status_code == 404


@pytest.mark.django_db
def test_score_history_returns_date_range(auth_client, user):
    DailyScoreFactory(user=user, date="2026-04-27", readiness_score=70)
    DailyScoreFactory(user=user, date="2026-04-28", readiness_score=80)
    DailyScoreFactory(user=user, date="2026-04-29", readiness_score=90)
    url = reverse("scores-history") + "?start=2026-04-27&end=2026-04-28"
    response = auth_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 2


@pytest.mark.django_db
def test_scores_are_scoped_to_authenticated_user(auth_client, user, db):
    from apps.users.tests.factories import UserFactory
    other_user = UserFactory()
    DailyScoreFactory(user=other_user, date=timezone.now().date(), readiness_score=99)
    response = auth_client.get(reverse("scores-today"))
    assert response.status_code == 404
```

- [ ] **Step 2: Write factory**

`backend/apps/health/tests/factories.py`:
```python
import factory
from factory.django import DjangoModelFactory
from apps.health.models import DailyScore
from apps.users.tests.factories import UserFactory


class DailyScoreFactory(DjangoModelFactory):
    class Meta:
        model = DailyScore

    user = factory.SubFactory(UserFactory)
    date = factory.Faker("date_this_year")
    readiness_score = factory.Faker("random_int", min=40, max=100)
    sleep_score = factory.Faker("random_int", min=40, max=100)
    recovery_score = factory.Faker("random_int", min=40, max=100)
    activity_score = factory.Faker("random_int", min=40, max=100)
    score_breakdown = factory.LazyFunction(dict)
```

- [ ] **Step 3: Write serializers and views**

`backend/apps/health/serializers.py`:
```python
from rest_framework import serializers
from .models import DailyScore, HealthMetric


class DailyScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyScore
        fields = ["id", "date", "readiness_score", "sleep_score", "recovery_score", "activity_score", "score_breakdown"]


class HealthMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthMetric
        fields = ["id", "metric_type", "value", "unit", "recorded_at"]
```

`backend/apps/health/views.py`:
```python
from django.utils import timezone
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.mixins import AuditMixin
from .models import DailyScore, HealthMetric
from .serializers import DailyScoreSerializer, HealthMetricSerializer


class TodayScoreView(AuditMixin, APIView):
    audit_resource_type = "DailyScore"

    def get(self, request: Request) -> Response:
        score = DailyScore.objects.filter(user=request.user, date=timezone.now().date()).first()
        if not score:
            return Response({"detail": "No score for today."}, status=status.HTTP_404_NOT_FOUND)
        self.log_read(request, str(score.pk))
        return Response(DailyScoreSerializer(score).data)


class ScoreHistoryView(AuditMixin, APIView):
    audit_resource_type = "DailyScore"

    def get(self, request: Request) -> Response:
        qs = DailyScore.objects.filter(user=request.user)
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)
        return Response(DailyScoreSerializer(qs, many=True).data)


class MetricsView(AuditMixin, APIView):
    audit_resource_type = "HealthMetric"

    def get(self, request: Request) -> Response:
        qs = HealthMetric.objects.filter(user=request.user)
        metric_type = request.query_params.get("type")
        start = request.query_params.get("start")
        end = request.query_params.get("end")
        if metric_type:
            qs = qs.filter(metric_type=metric_type)
        if start:
            qs = qs.filter(recorded_at__date__gte=start)
        if end:
            qs = qs.filter(recorded_at__date__lte=end)
        return Response(HealthMetricSerializer(qs[:500], many=True).data)
```

`backend/apps/health/urls.py`:
```python
from django.urls import path
from . import views

urlpatterns = [
    path("scores/today/", views.TodayScoreView.as_view(), name="scores-today"),
    path("scores/", views.ScoreHistoryView.as_view(), name="scores-history"),
    path("metrics/", views.MetricsView.as_view(), name="health-metrics"),
]
```

- [ ] **Step 4: Run tests -- expect pass**

```bash
pytest apps/health/tests/test_views.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add apps/health/
git commit -m "feat: dashboard scores and health metrics API"
```

---

## Task 8: Devices and Provider Access APIs (TDD)

**Files:**
- Create: `backend/apps/devices/serializers.py`, `views.py`, `urls.py`, `tests/test_views.py`
- Create: `backend/apps/providers/serializers.py`, `views.py`, `urls.py`, `tests/test_views.py`

- [ ] **Step 1: Write failing tests for devices API**

`backend/apps/devices/tests/test_views.py`:
```python
import pytest
from django.urls import reverse
from apps.devices.models import ConnectedDevice


@pytest.mark.django_db
def test_list_devices_returns_user_devices(auth_client, user):
    ConnectedDevice.objects.create(
        user=user, provider="whoop", access_token="tok", refresh_token="ref"
    )
    response = auth_client.get(reverse("devices-list"))
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["provider"] == "whoop"


@pytest.mark.django_db
def test_delete_device_removes_it(auth_client, user):
    device = ConnectedDevice.objects.create(
        user=user, provider="garmin", access_token="tok", refresh_token="ref"
    )
    response = auth_client.delete(reverse("devices-detail", args=[device.pk]))
    assert response.status_code == 204
    assert not ConnectedDevice.objects.filter(pk=device.pk).exists()


@pytest.mark.django_db
def test_cannot_delete_another_users_device(auth_client, db):
    from apps.users.tests.factories import UserFactory
    other_user = UserFactory()
    device = ConnectedDevice.objects.create(
        user=other_user, provider="fitbit", access_token="tok", refresh_token="ref"
    )
    response = auth_client.delete(reverse("devices-detail", args=[device.pk]))
    assert response.status_code == 404
```

- [ ] **Step 2: Implement devices API**

`backend/apps/devices/serializers.py`:
```python
from rest_framework import serializers
from .models import ConnectedDevice


class ConnectedDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectedDevice
        fields = ["id", "provider", "last_synced_at", "is_active", "created_at"]
```

`backend/apps/devices/views.py`:
```python
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ConnectedDevice
from .serializers import ConnectedDeviceSerializer


class DeviceListView(APIView):
    def get(self, request: Request) -> Response:
        devices = ConnectedDevice.objects.filter(user=request.user, is_active=True)
        return Response(ConnectedDeviceSerializer(devices, many=True).data)


class DeviceDetailView(APIView):
    def _get_device(self, pk: int, user):
        return ConnectedDevice.objects.filter(pk=pk, user=user).first()

    def delete(self, request: Request, pk: int) -> Response:
        device = self._get_device(pk, request.user)
        if not device:
            return Response(status=status.HTTP_404_NOT_FOUND)
        device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

`backend/apps/devices/urls.py`:
```python
from django.urls import path
from . import views

urlpatterns = [
    path("devices/", views.DeviceListView.as_view(), name="devices-list"),
    path("devices/<int:pk>/", views.DeviceDetailView.as_view(), name="devices-detail"),
]
```

- [ ] **Step 3: Write failing tests for provider access**

`backend/apps/providers/tests/test_views.py`:
```python
import pytest
from django.urls import reverse
from apps.providers.models import ProviderAccess


@pytest.mark.django_db
def test_grant_provider_access(auth_client, user):
    response = auth_client.post(reverse("provider-access-list"), {
        "provider_name": "Dr. Smith",
        "provider_email": "drsmith@clinic.com",
        "provider_type": "physician",
        "access_level": "read_summary",
    }, format="json")
    assert response.status_code == 201
    assert ProviderAccess.objects.filter(patient=user).count() == 1


@pytest.mark.django_db
def test_revoke_provider_access(auth_client, user):
    access = ProviderAccess.objects.create(
        patient=user,
        provider_name="Dr. Jones",
        provider_email="drjones@clinic.com",
    )
    response = auth_client.delete(reverse("provider-access-detail", args=[access.pk]))
    assert response.status_code == 204
    access.refresh_from_db()
    assert access.revoked_at is not None
```

- [ ] **Step 4: Implement provider access API**

`backend/apps/providers/serializers.py`:
```python
from rest_framework import serializers
from .models import ProviderAccess


class ProviderAccessSerializer(serializers.ModelSerializer):
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = ProviderAccess
        fields = ["id", "provider_name", "provider_email", "provider_type",
                  "access_level", "authorized_at", "expires_at", "is_active"]
        read_only_fields = ["id", "authorized_at", "is_active"]
```

`backend/apps/providers/views.py`:
```python
from django.utils import timezone
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.audit.mixins import AuditMixin
from .models import ProviderAccess
from .serializers import ProviderAccessSerializer


class ProviderAccessListView(AuditMixin, APIView):
    audit_resource_type = "ProviderAccess"

    def get(self, request: Request) -> Response:
        accesses = ProviderAccess.objects.filter(patient=request.user)
        return Response(ProviderAccessSerializer(accesses, many=True).data)

    def post(self, request: Request) -> Response:
        serializer = ProviderAccessSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access = serializer.save(patient=request.user)
        self.log_write(request, str(access.pk))
        return Response(ProviderAccessSerializer(access).data, status=status.HTTP_201_CREATED)


class ProviderAccessDetailView(AuditMixin, APIView):
    audit_resource_type = "ProviderAccess"

    def delete(self, request: Request, pk: int) -> Response:
        access = ProviderAccess.objects.filter(pk=pk, patient=request.user).first()
        if not access:
            return Response(status=status.HTTP_404_NOT_FOUND)
        access.revoked_at = timezone.now()
        access.save(update_fields=["revoked_at"])
        self.log_delete(request, str(pk))
        return Response(status=status.HTTP_204_NO_CONTENT)
```

`backend/apps/providers/urls.py`:
```python
from django.urls import path
from . import views

urlpatterns = [
    path("provider-access/", views.ProviderAccessListView.as_view(), name="provider-access-list"),
    path("provider-access/<int:pk>/", views.ProviderAccessDetailView.as_view(), name="provider-access-detail"),
]
```

- [ ] **Step 5: Run all tests**

```bash
pytest apps/devices/tests/ apps/providers/tests/ -v
```

Expected: `5 passed`

- [ ] **Step 6: Commit**

```bash
git add apps/devices/ apps/providers/
git commit -m "feat: devices and provider access APIs"
```

---

## Task 9: Claude AI Service and Endpoints (TDD)

**Files:**
- Create: `backend/apps/ai/services.py`
- Create: `backend/apps/ai/serializers.py`
- Create: `backend/apps/ai/views.py`
- Create: `backend/apps/ai/urls.py`
- Create: `backend/apps/ai/tests/test_services.py`
- Create: `backend/apps/ai/tests/test_views.py`

- [ ] **Step 1: Write failing service tests**

`backend/apps/ai/tests/test_services.py`:
```python
import pytest
from unittest.mock import patch, MagicMock
from apps.ai.services import AIService, ModelRoute


def test_chat_routes_to_haiku():
    service = AIService.__new__(AIService)
    assert service._model_for(ModelRoute.CHAT) == "claude-haiku-4-5-20251001"


def test_insights_routes_to_sonnet():
    service = AIService.__new__(AIService)
    assert service._model_for(ModelRoute.INSIGHTS) == "claude-sonnet-4-6"


@pytest.mark.django_db
def test_ai_service_sends_user_context(user):
    with patch("apps.ai.services.anthropic.Anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="Here are your insights.")],
            model="claude-haiku-4-5-20251001",
        )
        service = AIService(api_key="test-key")
        result = service.chat(user=user, messages=[{"role": "user", "content": "How am I doing?"}])
        assert "Here are your insights." in result
        call_kwargs = mock_client.messages.create.call_args[1]
        assert "BioIQ" in call_kwargs["system"]
```

- [ ] **Step 2: Implement AIService**

`backend/apps/ai/services.py`:
```python
from enum import Enum
from typing import Any
import anthropic
from django.conf import settings


class ModelRoute(str, Enum):
    CHAT = "chat"
    INSIGHTS = "insights"
    QUESTIONS = "questions"
    WORKOUT = "workout"


MODEL_MAP = {
    ModelRoute.CHAT: "claude-haiku-4-5-20251001",
    ModelRoute.QUESTIONS: "claude-haiku-4-5-20251001",
    ModelRoute.INSIGHTS: "claude-sonnet-4-6",
    ModelRoute.WORKOUT: "claude-sonnet-4-6",
}

SYSTEM_PROMPT = """You are BioIQ AI, a personal health intelligence assistant.
You have access to the user health data provided below. Use it to give personalized,
evidence-based guidance. Be clear, supportive, and appropriately cautious -- always
recommend consulting a healthcare professional for medical decisions.

Never fabricate health data. If you are uncertain, say so."""


class AIService:
    def __init__(self, api_key: str | None = None) -> None:
        self.client = anthropic.Anthropic(api_key=api_key or settings.ANTHROPIC_API_KEY)

    def _model_for(self, route: ModelRoute) -> str:
        return MODEL_MAP[route]

    def _build_system_prompt(self, user) -> str:
        from apps.health.models import DailyScore
        from django.utils import timezone

        context_lines = [SYSTEM_PROMPT, f"\nUser: {user.first_name} {user.last_name}"]
        try:
            profile = user.health_profile
            if profile.date_of_birth:
                context_lines.append(f"Date of birth: {profile.date_of_birth}")
            if profile.fitness_goals:
                context_lines.append(f"Fitness goals: {', '.join(profile.fitness_goals)}")
        except Exception:
            pass

        recent_scores = DailyScore.objects.filter(user=user).order_by("-date")[:7]
        if recent_scores:
            context_lines.append("\nRecent readiness scores (last 7 days):")
            for score in recent_scores:
                context_lines.append(f"  {score.date}: {score.readiness_score}/100")

        return "\n".join(context_lines)

    def _call(self, route: ModelRoute, user, messages: list[dict[str, Any]]) -> str:
        safe_messages = [
            {"role": m["role"], "content": str(m["content"])[:4000]}
            for m in messages
        ]
        response = self.client.messages.create(
            model=self._model_for(route),
            max_tokens=1024,
            system=self._build_system_prompt(user),
            messages=safe_messages,
        )
        return response.content[0].text

    def chat(self, user, messages: list[dict[str, Any]]) -> str:
        return self._call(ModelRoute.CHAT, user, messages)

    def insights(self, user, messages: list[dict[str, Any]]) -> str:
        return self._call(ModelRoute.INSIGHTS, user, messages)

    def compile_questions(self, user, messages: list[dict[str, Any]]) -> str:
        return self._call(ModelRoute.QUESTIONS, user, messages)

    def workout_plan(self, user, messages: list[dict[str, Any]]) -> str:
        return self._call(ModelRoute.WORKOUT, user, messages)
```

- [ ] **Step 3: Write failing view tests**

`backend/apps/ai/tests/test_views.py`:
```python
import pytest
from django.urls import reverse
from unittest.mock import patch


@pytest.mark.django_db
def test_chat_endpoint_returns_ai_response(auth_client):
    with patch("apps.ai.views.AIService") as mock_service_class:
        mock_service_class.return_value.chat.return_value = "Here is my response."
        response = auth_client.post(reverse("ai-chat"), {
            "messages": [{"role": "user", "content": "How is my sleep?"}]
        }, format="json")
    assert response.status_code == 200
    assert response.data["reply"] == "Here is my response."


@pytest.mark.django_db
def test_insights_endpoint_requires_auth(api_client):
    response = api_client.post(reverse("ai-insights"), {}, format="json")
    assert response.status_code == 401
```

- [ ] **Step 4: Write AI views**

`backend/apps/ai/serializers.py`:
```python
from rest_framework import serializers
from .models import AIConversation


class MessageSerializer(serializers.Serializer):
    messages = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=50,
    )


class AIConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIConversation
        fields = ["id", "messages", "conversation_type", "model_used", "created_at", "updated_at"]
```

`backend/apps/ai/views.py`:
```python
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from .services import AIService
from .models import AIConversation
from .serializers import MessageSerializer, AIConversationSerializer


def _save_conversation(user, messages: list, reply: str, conv_type: str, model: str) -> None:
    all_messages = messages + [{"role": "assistant", "content": reply}]
    AIConversation.objects.create(
        user=user,
        messages=all_messages,
        conversation_type=conv_type,
        model_used=model,
    )


class ChatView(APIView):
    def post(self, request: Request) -> Response:
        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        messages = serializer.validated_data["messages"]
        service = AIService()
        reply = service.chat(user=request.user, messages=messages)
        _save_conversation(request.user, messages, reply, AIConversation.ConversationType.CHAT, "claude-haiku-4-5-20251001")
        return Response({"reply": reply})


class InsightsView(APIView):
    def post(self, request: Request) -> Response:
        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        messages = serializer.validated_data["messages"]
        service = AIService()
        reply = service.insights(user=request.user, messages=messages)
        _save_conversation(request.user, messages, reply, AIConversation.ConversationType.INSIGHTS, "claude-sonnet-4-6")
        return Response({"reply": reply})


class QuestionsView(APIView):
    def post(self, request: Request) -> Response:
        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        messages = serializer.validated_data["messages"]
        service = AIService()
        reply = service.compile_questions(user=request.user, messages=messages)
        _save_conversation(request.user, messages, reply, AIConversation.ConversationType.QUESTIONS, "claude-haiku-4-5-20251001")
        return Response({"reply": reply})


class WorkoutPlanView(APIView):
    def post(self, request: Request) -> Response:
        serializer = MessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        messages = serializer.validated_data["messages"]
        service = AIService()
        reply = service.workout_plan(user=request.user, messages=messages)
        _save_conversation(request.user, messages, reply, AIConversation.ConversationType.WORKOUT, "claude-sonnet-4-6")
        return Response({"reply": reply})


class ConversationHistoryView(APIView):
    def get(self, request: Request) -> Response:
        conversations = AIConversation.objects.filter(user=request.user)[:20]
        return Response(AIConversationSerializer(conversations, many=True).data)
```

`backend/apps/ai/urls.py`:
```python
from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.ChatView.as_view(), name="ai-chat"),
    path("chat/history/", views.ConversationHistoryView.as_view(), name="ai-chat-history"),
    path("insights/", views.InsightsView.as_view(), name="ai-insights"),
    path("questions/", views.QuestionsView.as_view(), name="ai-questions"),
    path("workout/plan/", views.WorkoutPlanView.as_view(), name="ai-workout-plan"),
]
```

- [ ] **Step 5: Run tests -- expect pass**

```bash
pytest apps/ai/tests/ -v
```

Expected: `3 passed`

- [ ] **Step 6: Run full backend test suite**

```bash
pytest --cov=apps --cov-fail-under=80 -v
```

Expected: All tests pass, coverage >= 80%.

- [ ] **Step 7: Commit**

```bash
git add apps/ai/
git commit -m "feat: Claude AI service with Haiku/Sonnet routing and conversation endpoints"
```

---

## Task 10: Next.js Frontend Setup

**Files:**
- Create: `frontend/package.json`, `tsconfig.json`, `next.config.ts`, `.env.example`
- Create: `frontend/src/lib/api.ts`, `auth.ts`, `utils.ts`
- Create: `frontend/src/types/index.ts`
- Create: `frontend/src/app/layout.tsx`, `globals.css`
- Create: `frontend/src/components/layout/QueryProvider.tsx`

- [ ] **Step 1: Initialize Next.js project**

```bash
cd frontend
npx create-next-app@14 . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
npm install @tanstack/react-query axios framer-motion recharts
npm install @radix-ui/react-slot class-variance-authority clsx tailwind-merge lucide-react
npm install -D @testing-library/react @testing-library/jest-dom jest jest-environment-jsdom
```

- [ ] **Step 2: Write frontend/.env.example**

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

- [ ] **Step 3: Write src/types/index.ts**

```typescript
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_verified: boolean;
  health_profile: HealthProfile | null;
}

export interface HealthProfile {
  date_of_birth: string | null;
  biological_sex: string;
  height_cm: number | null;
  weight_kg: string | null;
  fitness_goals: string[];
}

export interface DailyScore {
  id: number;
  date: string;
  readiness_score: number;
  sleep_score: number | null;
  recovery_score: number | null;
  activity_score: number | null;
  score_breakdown: Record<string, number>;
}

export interface AIMessage {
  role: "user" | "assistant";
  content: string;
}
```

- [ ] **Step 4: Write src/lib/utils.ts**

```typescript
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getScoreColor(score: number): string {
  if (score >= 80) return "text-emerald-400";
  if (score >= 60) return "text-amber-400";
  return "text-rose-400";
}

export function getScoreLabel(score: number): string {
  if (score >= 80) return "Optimal";
  if (score >= 60) return "Good";
  if (score >= 40) return "Moderate";
  return "Low";
}
```

- [ ] **Step 5: Write src/lib/api.ts**

```typescript
import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,
});

let accessToken: string | null = null;

export function setAccessToken(token: string | null) {
  accessToken = token;
}

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = "Bearer " + accessToken;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const res = await axios.post(
          process.env.NEXT_PUBLIC_API_URL + "/api/auth/token/refresh/",
          {},
          { withCredentials: true }
        );
        setAccessToken(res.data.access);
        original.headers.Authorization = "Bearer " + res.data.access;
        return api(original);
      } catch {
        setAccessToken(null);
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);
```

- [ ] **Step 6: Write src/lib/auth.ts**

```typescript
"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { api, setAccessToken } from "./api";
import type { User } from "@/types";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.post("/api/auth/token/refresh/")
      .then((res) => { setAccessToken(res.data.access); return api.get<User>("/api/auth/me/"); })
      .then((res) => setUser(res.data))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  async function login(email: string, password: string) {
    const res = await api.post("/api/auth/login/", { email, password });
    setAccessToken(res.data.access);
    const me = await api.get<User>("/api/auth/me/");
    setUser(me.data);
  }

  async function logout() {
    await api.post("/api/auth/logout/");
    setAccessToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
```

- [ ] **Step 7: Write layout.tsx and QueryProvider**

`frontend/src/components/layout/QueryProvider.tsx`:
```typescript
"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export default function QueryProvider({ children }: { children: React.ReactNode }) {
  const [client] = useState(() => new QueryClient({
    defaultOptions: { queries: { staleTime: 60_000, retry: 1 } },
  }));
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
```

`frontend/src/app/layout.tsx`:
```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";
import QueryProvider from "@/components/layout/QueryProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "BioIQ",
  description: "Your personal health intelligence hub",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className + " bg-slate-950 text-slate-100 antialiased"}>
        <QueryProvider>
          <AuthProvider>{children}</AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
```

- [ ] **Step 8: Verify build**

```bash
cd frontend
npm run build
```

Expected: Build completes with no type errors.

- [ ] **Step 9: Commit**

```bash
git add frontend/
git commit -m "feat: Next.js frontend setup with auth context, API client, TanStack Query"
```

---

## Task 11: Dashboard Page (ReadinessScore + MetricCards)

**Files:**
- Create: `frontend/src/components/dashboard/ReadinessScore.tsx`
- Create: `frontend/src/components/dashboard/MetricCard.tsx`
- Create: `frontend/src/components/layout/NavBar.tsx`
- Create: `frontend/src/components/layout/AppShell.tsx`
- Create: `frontend/src/app/(app)/dashboard/page.tsx`
- Create: `frontend/__tests__/ReadinessScore.test.tsx`

- [ ] **Step 1: Write failing test**

`frontend/__tests__/ReadinessScore.test.tsx`:
```typescript
import { render, screen } from "@testing-library/react";
import ReadinessScore from "@/components/dashboard/ReadinessScore";

describe("ReadinessScore", () => {
  it("displays the score number", () => {
    render(<ReadinessScore score={82} label="Optimal" color="text-emerald-400" />);
    expect(screen.getByText("82")).toBeInTheDocument();
    expect(screen.getByText("Optimal")).toBeInTheDocument();
  });
  it("renders low score", () => {
    render(<ReadinessScore score={35} label="Low" color="text-rose-400" />);
    expect(screen.getByText("35")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test -- expect failure**

```bash
npx jest __tests__/ReadinessScore.test.tsx
```

Expected: `Cannot find module @/components/dashboard/ReadinessScore`

- [ ] **Step 3: Write ReadinessScore component**

`frontend/src/components/dashboard/ReadinessScore.tsx`:
```typescript
"use client";
import { motion } from "framer-motion";

interface Props { score: number; label: string; color: string; }

export default function ReadinessScore({ score, label, color }: Props) {
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative">
        <svg width="200" height="200" className="-rotate-90">
          <circle cx="100" cy="100" r={radius} fill="none" stroke="#1e293b" strokeWidth="12" />
          <motion.circle cx="100" cy="100" r={radius} fill="none" stroke="currentColor"
            strokeWidth="12" strokeLinecap="round" strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }} animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.2, ease: "easeOut" }} className={color} />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span className="text-5xl font-bold text-white"
            initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4, duration: 0.5 }}>
            {score}
          </motion.span>
          <span className="text-sm text-slate-400">/ 100</span>
        </div>
      </div>
      <span className={"text-lg font-semibold " + color}>{label}</span>
      <p className="text-slate-400 text-sm">Daily Readiness</p>
    </div>
  );
}
```

- [ ] **Step 4: Write MetricCard component**

`frontend/src/components/dashboard/MetricCard.tsx`:
```typescript
"use client";
import { motion } from "framer-motion";

interface Props { title: string; value: number | null; icon: React.ReactNode; delay?: number; }

export default function MetricCard({ title, value, icon, delay = 0 }: Props) {
  return (
    <motion.div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col gap-3"
      initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}>
      <div className="flex items-center justify-between">
        <span className="text-slate-400 text-sm font-medium">{title}</span>
        <span className="text-slate-500">{icon}</span>
      </div>
      <span className="text-3xl font-bold text-white">{value ?? "--"}</span>
    </motion.div>
  );
}
```

- [ ] **Step 5: Write NavBar and AppShell**

`frontend/src/components/layout/NavBar.tsx`:
```typescript
"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";

const links = [
  { href: "/dashboard", label: "Home" },
  { href: "/metrics", label: "Metrics" },
  { href: "/devices", label: "Devices" },
  { href: "/ai", label: "BioIQ AI" },
  { href: "/providers", label: "Providers" },
  { href: "/settings", label: "Settings" },
];

export default function NavBar() {
  const pathname = usePathname();
  const { logout } = useAuth();
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-950/80 backdrop-blur border-b border-slate-800">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <span className="text-xl font-bold text-white tracking-tight">BioIQ</span>
        <div className="flex items-center gap-6">
          {links.map((link) => (
            <Link key={link.href} href={link.href}
              className={cn("text-sm font-medium transition-colors",
                pathname.startsWith(link.href) ? "text-white" : "text-slate-400 hover:text-white")}>
              {link.label}
            </Link>
          ))}
          <button onClick={logout} className="text-sm text-slate-400 hover:text-white transition-colors">
            Sign out
          </button>
        </div>
      </div>
    </nav>
  );
}
```

`frontend/src/components/layout/AppShell.tsx`:
```typescript
import NavBar from "./NavBar";
export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-950">
      <NavBar />
      <main className="max-w-6xl mx-auto px-4 pt-24 pb-16">{children}</main>
    </div>
  );
}
```

- [ ] **Step 6: Write Dashboard page**

`frontend/src/app/(app)/dashboard/page.tsx`:
```typescript
"use client";
import { useQuery } from "@tanstack/react-query";
import { Heart, Moon, Activity, Zap } from "lucide-react";
import { api } from "@/lib/api";
import AppShell from "@/components/layout/AppShell";
import ReadinessScore from "@/components/dashboard/ReadinessScore";
import MetricCard from "@/components/dashboard/MetricCard";
import { getScoreColor, getScoreLabel } from "@/lib/utils";
import type { DailyScore } from "@/types";

export default function DashboardPage() {
  const { data: score, isLoading, isError } = useQuery<DailyScore>({
    queryKey: ["scores", "today"],
    queryFn: () => api.get("/api/scores/today/").then((r) => r.data),
  });

  return (
    <AppShell>
      <div className="flex flex-col items-center gap-12">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white mb-2">Good morning</h1>
          <p className="text-slate-400">Your health snapshot for today.</p>
        </div>
        {isLoading && <p className="text-slate-400">Loading...</p>}
        {isError && (
          <div className="text-center">
            <p className="text-slate-500">No data for today. Connect a device to get started.</p>
          </div>
        )}
        {score && (
          <>
            <ReadinessScore score={score.readiness_score}
              label={getScoreLabel(score.readiness_score)}
              color={getScoreColor(score.readiness_score)} />
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full">
              <MetricCard title="Sleep" value={score.sleep_score} icon={<Moon size={18} />} delay={0.1} />
              <MetricCard title="Recovery" value={score.recovery_score} icon={<Heart size={18} />} delay={0.2} />
              <MetricCard title="Activity" value={score.activity_score} icon={<Activity size={18} />} delay={0.3} />
              <MetricCard title="Readiness" value={score.readiness_score} icon={<Zap size={18} />} delay={0.4} />
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
```

- [ ] **Step 7: Run component tests**

```bash
npx jest --passWithNoTests
```

Expected: `2 passed`

- [ ] **Step 8: Commit**

```bash
git add frontend/
git commit -m "feat: dashboard page with animated ReadinessScore ring and MetricCards"
```

---

## Task 12: Auth Pages and Remaining Page Shells

**Files:**
- Create: `frontend/src/app/(auth)/login/page.tsx`
- Create: `frontend/src/app/(auth)/register/page.tsx`
- Create: `frontend/src/app/(auth)/reset/page.tsx`
- Create: `frontend/src/app/(app)/metrics/page.tsx`
- Create: `frontend/src/app/(app)/devices/page.tsx`
- Create: `frontend/src/app/(app)/ai/page.tsx`
- Create: `frontend/src/app/(app)/providers/page.tsx`
- Create: `frontend/src/app/(app)/settings/page.tsx`

- [ ] **Step 1: Write login page**

`frontend/src/app/(auth)/login/page.tsx`:
```typescript
"use client";
import Link from "next/link";
import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch {
      setError("Invalid email or password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">BioIQ</h1>
          <p className="text-slate-400">Your health intelligence hub</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
          <h2 className="text-xl font-semibold text-white mb-6">Sign in</h2>
          {error && <p className="text-rose-400 text-sm mb-4 bg-rose-950 border border-rose-800 rounded-lg p-3">{error}</p>}
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
              <label className="text-sm text-slate-400">Email</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
                className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-blue-500"
                placeholder="you@example.com" />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm text-slate-400">Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required
                className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-blue-500" />
            </div>
            <button type="submit" disabled={loading}
              className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold rounded-lg py-2.5 transition-colors">
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>
          <p className="text-center text-sm text-slate-400 mt-6">
            No account? <Link href="/register" className="text-blue-400 hover:text-blue-300">Create one</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Write register page**

`frontend/src/app/(auth)/register/page.tsx`:
```typescript
"use client";
import Link from "next/link";
import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { api, setAccessToken } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", password: "", first_name: "", last_name: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post("/api/auth/register/", form);
      setAccessToken(res.data.access);
      router.push("/dashboard");
    } catch {
      setError("Registration failed. Please check your details and try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">BioIQ</h1>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8">
          <h2 className="text-xl font-semibold text-white mb-6">Create account</h2>
          {error && <p className="text-rose-400 text-sm mb-4">{error}</p>}
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="flex flex-col gap-1">
                <label className="text-sm text-slate-400">First name</label>
                <input type="text" value={form.first_name} onChange={(e) => setForm({...form, first_name: e.target.value})}
                  className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-blue-500" />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-sm text-slate-400">Last name</label>
                <input type="text" value={form.last_name} onChange={(e) => setForm({...form, last_name: e.target.value})}
                  className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-blue-500" />
              </div>
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm text-slate-400">Email</label>
              <input type="email" value={form.email} required onChange={(e) => setForm({...form, email: e.target.value})}
                className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-blue-500" />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm text-slate-400">Password (12+ characters)</label>
              <input type="password" value={form.password} required onChange={(e) => setForm({...form, password: e.target.value})}
                className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-blue-500" />
            </div>
            <button type="submit" disabled={loading}
              className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold rounded-lg py-2.5 transition-colors">
              {loading ? "Creating account..." : "Create account"}
            </button>
          </form>
          <p className="text-center text-sm text-slate-400 mt-6">
            Already have an account? <Link href="/login" className="text-blue-400 hover:text-blue-300">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Write password reset page**

`frontend/src/app/(auth)/reset/page.tsx`:
```typescript
"use client";
import Link from "next/link";
import { useState, FormEvent } from "react";
import { api } from "@/lib/api";

export default function ResetPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try { await api.post("/api/auth/password/reset/", { email }); } finally {
      setSent(true);
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-sm bg-slate-900 border border-slate-800 rounded-2xl p-8">
        <h2 className="text-xl font-semibold text-white mb-4">Reset password</h2>
        {sent ? (
          <p className="text-slate-300 text-sm">If that email exists, a reset link is on its way.</p>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
              placeholder="you@example.com"
              className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-blue-500" />
            <button type="submit" disabled={loading}
              className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold rounded-lg py-2.5 transition-colors">
              {loading ? "Sending..." : "Send reset link"}
            </button>
          </form>
        )}
        <p className="text-center text-sm text-slate-400 mt-6">
          <Link href="/login" className="text-blue-400 hover:text-blue-300">Back to sign in</Link>
        </p>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Write remaining page shells**

`frontend/src/app/(app)/metrics/page.tsx`:
```typescript
import AppShell from "@/components/layout/AppShell";
export default function MetricsPage() {
  return <AppShell><h1 className="text-2xl font-bold text-white mb-4">Health Metrics</h1>
    <p className="text-slate-400">Your metric history and trends will appear here once a device is connected.</p></AppShell>;
}
```

`frontend/src/app/(app)/devices/page.tsx`:
```typescript
import AppShell from "@/components/layout/AppShell";
export default function DevicesPage() {
  return <AppShell><h1 className="text-2xl font-bold text-white mb-4">Connected Devices</h1>
    <p className="text-slate-400">Connect Whoop, Apple Health, Garmin, Fitbit, or Strava.</p></AppShell>;
}
```

`frontend/src/app/(app)/ai/page.tsx`:
```typescript
import AppShell from "@/components/layout/AppShell";
export default function AIPage() {
  return <AppShell><h1 className="text-2xl font-bold text-white mb-4">BioIQ AI</h1>
    <p className="text-slate-400">Health insights and workout plans powered by Claude -- coming in the next release.</p></AppShell>;
}
```

`frontend/src/app/(app)/providers/page.tsx`:
```typescript
import AppShell from "@/components/layout/AppShell";
export default function ProvidersPage() {
  return <AppShell><h1 className="text-2xl font-bold text-white mb-4">Healthcare Providers</h1>
    <p className="text-slate-400">Grant secure read access to your physicians and health coaches.</p></AppShell>;
}
```

`frontend/src/app/(app)/settings/page.tsx`:
```typescript
import AppShell from "@/components/layout/AppShell";
export default function SettingsPage() {
  return <AppShell><h1 className="text-2xl font-bold text-white mb-4">Settings</h1>
    <p className="text-slate-400">Profile and account management coming in the next release.</p></AppShell>;
}
```

- [ ] **Step 5: Build verify**

```bash
cd frontend && npm run build
```

Expected: Build completes with no errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/
git commit -m "feat: auth pages and remaining page shells"
```

---

## Task 13: GitHub Actions CI Pipeline

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Write CI pipeline**

`.github/workflows/ci.yml`:
```yaml
name: CI

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main, staging]

jobs:
  lint:
    name: Lint and Format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff
      - run: ruff check backend/
      - run: ruff format --check backend/
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: cd frontend && npm ci && npm run lint

  type-check:
    name: Type Check
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r backend/requirements-dev.txt
      - run: cd backend && mypy apps/
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: cd frontend && npm ci && npx tsc --noEmit

  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install bandit pip-audit
      - run: bandit -r backend/apps/ -ll
      - run: pip-audit -r backend/requirements.txt
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: cd frontend && npm ci && npm audit --audit-level=high

  test:
    name: Test Suite
    runs-on: ubuntu-latest
    needs: [type-check, security-scan]
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: bioiq
          POSTGRES_PASSWORD: bioiq
          POSTGRES_DB: bioiq_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r backend/requirements-dev.txt
      - name: Run Django tests
        run: cd backend && pytest --cov-fail-under=80
        env:
          DB_HOST: localhost
          DB_PORT: "5432"
          DB_NAME: bioiq_test
          DB_USER: bioiq
          DB_PASSWORD: bioiq
          SECRET_KEY: ci-key-not-for-production-use-only
          DJANGO_SETTINGS_MODULE: bioiq.settings.local
          FIELD_ENCRYPTION_KEY: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
          ANTHROPIC_API_KEY: test-key
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: cd frontend && npm ci && npm test -- --coverage --watchAll=false --passWithNoTests

  build:
    name: Build Check
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r backend/requirements.txt
      - name: Django system check
        run: cd backend && python manage.py check
        env:
          DB_HOST: localhost
          DB_NAME: placeholder
          DB_USER: placeholder
          DB_PASSWORD: placeholder
          SECRET_KEY: build-check-placeholder-not-real
          DJANGO_SETTINGS_MODULE: bioiq.settings.local
          FIELD_ENCRYPTION_KEY: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Next.js build
        run: cd frontend && npm ci && npm run build
        env:
          NEXT_PUBLIC_API_URL: https://api.bioiq.app
```

- [ ] **Step 2: Configure GitHub branch protection**

In GitHub repo Settings > Branches > Add rule for `main` and `staging`:
- Require status checks: `lint`, `type-check`, `security-scan`, `test`, `build`
- Require pull request before merging (1 approval minimum)
- Do not allow bypassing the settings

- [ ] **Step 3: Commit**

```bash
git add .github/
git commit -m "feat: GitHub Actions CI -- 5 stages: lint, type-check, security, test, build"
```

---

## Task 14: AWS and Vercel Deployment

**Files:**
- Create: `frontend/vercel.json`

- [ ] **Step 1: Sign the AWS HIPAA Business Associate Agreement (BAA)**

In the AWS Console:
1. Search for "AWS Artifact"
2. Navigate to "Agreements"
3. Locate "AWS Business Associate Addendum"
4. Click "Accept agreement" -- this is free and required before storing any PHI

- [ ] **Step 2: Launch EC2 instance (free tier)**

In AWS Console > EC2 > Launch instance:
- Name: `bioiq-backend`
- AMI: Ubuntu 22.04 LTS
- Instance type: `t2.micro` (free tier eligible)
- Key pair: Create new, download `.pem`, store securely (cannot be recovered if lost)
- Security group inbound rules: SSH port 22 (your IP only), HTTP port 80, HTTPS port 443
- Storage: 8 GB gp3

- [ ] **Step 3: Launch RDS PostgreSQL (free tier)**

In AWS Console > RDS > Create database:
- Engine: PostgreSQL 16
- Template: Free tier
- DB identifier: `bioiq-db`
- Master username: `bioiq`
- Master password: generate with a password manager, save it
- Instance: `db.t3.micro`
- Storage: 20 GB gp2
- Public access: No
- VPC: same VPC as EC2

Note the RDS endpoint hostname shown after creation.

- [ ] **Step 4: Create S3 bucket for file storage**

In AWS Console > S3 > Create bucket:
- Bucket name: `bioiq-files-ACCOUNTID` (replace ACCOUNTID with your 12-digit AWS account number)
- Region: `us-east-1`
- Block all public access: Yes (all four checkboxes)
- Versioning: Enabled
- Default encryption: Amazon S3 managed keys (SSE-S3)

- [ ] **Step 5: Store production secrets in AWS Secrets Manager**

In AWS Console > Secrets Manager > Store a new secret:
- Secret type: Other type of secret
- Add key/value pairs:
  - `SECRET_KEY`: generate a 50-character random string
  - `DB_PASSWORD`: the RDS password from Step 3
  - `ANTHROPIC_API_KEY`: from console.anthropic.com
  - `FIELD_ENCRYPTION_KEY`: a 64-character hex string (run: python3 -c "import secrets; print(secrets.token_hex(32))")
- Secret name: `bioiq/production`

- [ ] **Step 6: Install Django on EC2 and configure Gunicorn**

SSH to EC2:
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

On the EC2 instance:
```bash
sudo apt-get update && sudo apt-get install -y python3-pip python3-venv nginx
git clone https://github.com/YOUR_USERNAME/bioiq.git /home/ubuntu/bioiq
cd /home/ubuntu/bioiq/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt gunicorn
```

Create `/etc/systemd/system/bioiq.service` with these contents:
```ini
[Unit]
Description=BioIQ Gunicorn
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/bioiq/backend
EnvironmentFile=/home/ubuntu/bioiq/backend/.env
ExecStart=/home/ubuntu/bioiq/backend/.venv/bin/gunicorn bioiq.wsgi:application --bind 127.0.0.1:8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable bioiq && sudo systemctl start bioiq
```

- [ ] **Step 7: Run migrations on EC2**

```bash
cd /home/ubuntu/bioiq/backend && source .venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
```

Expected: All migrations applied, superuser created.

- [ ] **Step 8: Deploy frontend to Vercel**

On your local machine:
```bash
cd frontend
npx vercel
```

Follow prompts: project name `bioiq-frontend`, set env var `NEXT_PUBLIC_API_URL` to `https://YOUR_EC2_IP_OR_DOMAIN`.

After deployment, copy the Vercel URL and add it to `CORS_ALLOWED_ORIGINS` in production settings.

- [ ] **Step 9: Write vercel.json**

`frontend/vercel.json`:
```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.bioiq.app"
  }
}
```

- [ ] **Step 10: Verify end-to-end**

1. Open the Vercel URL in a browser
2. Register an account
3. Log in and confirm dashboard loads
4. Check EC2 logs: `sudo journalctl -u bioiq -f`

Expected: No errors in logs, full auth flow works.

- [ ] **Step 11: Commit**

```bash
git add frontend/vercel.json
git commit -m "feat: Vercel deployment config for Next.js frontend"
git push origin main
```

---

## Self-Review Notes

**Spec coverage check:**
- Architecture: Covered in Tasks 1-2 (project setup, Docker, settings)
- Data model (all 8 entities): Covered in Tasks 3-5
- Auth (JWT + social): Task 6 covers JWT. Social auth (Apple/Google) is wired via django-allauth in settings/installed apps but the social callback views rely on allauth defaults -- no custom task needed as allauth handles the OAuth flow automatically once credentials are in .env
- HIPAA/AuditLog: Task 4
- API endpoints (all from spec): Tasks 7-9
- AI layer (Claude Haiku/Sonnet routing): Task 9
- Frontend (Next.js + dashboard + auth pages): Tasks 10-12
- CI/CD (5 stages): Task 13
- AWS + Vercel deployment: Task 14
- OWASP controls: Baked into implementation choices throughout (ORM-only queries, JWT, HTTPS-enforced settings, audit logging, input validation via DRF serializers)
- Three environments (local/staging/prod): Settings files in Task 2, Docker Compose in Task 1

**Placeholder scan:** No TBDs, no TODOs, no "add error handling here" comments found.

**Type consistency:** All model field names, serializer fields, and view imports reference consistent names across tasks. `DailyScore`, `HealthMetric`, `ConnectedDevice`, `ProviderAccess`, `AIConversation`, `AuditLog` are consistent from model definition through serializer through view through URL.

**Note on Apple Developer account:** Social auth via Sign in with Apple requires Apple Developer Program membership ($99/year). During development and testing, use email/password and Google OAuth only. The allauth Apple provider is installed and configured in settings but Apple credentials can be left blank in .env until ready to enable. This does not block any other development work.

"""Base Django settings for BimaGrid."""

from __future__ import annotations

import os
from pathlib import Path

import environ


BASE_DIR = Path(__file__).resolve().parents[3]
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="django-insecure-bimagrid-development-secret-key")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
	"corsheaders",
	"django.contrib.admin",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sessions",
	"django.contrib.messages",
	"django.contrib.staticfiles",
	"rest_framework.authtoken",
	"rest_framework",
	"django_filters",
	"apps.core",
	"apps.accounts",
	"apps.onboarding",
	"apps.policies",
	"apps.pricing",
	"apps.oracles",
	"apps.verification",
	"apps.payments",
	"apps.claims",
	"apps.notifications",
	"apps.geospatial",
	"apps.satellite",
	"apps.admin_dashboard",
	"apps.ussd",
]

MIDDLEWARE = [
	"django.middleware.security.SecurityMiddleware",
	"apps.core.middleware.RequestIDMiddleware",
	"middleware.logging.RequestTimingMiddleware",
	"middleware.rate_limiting.SimpleRateLimitMiddleware",
	"middleware.authentication.InternalApiKeyMiddleware",
	"whitenoise.middleware.WhiteNoiseMiddleware",
	"corsheaders.middleware.CorsMiddleware",
	"django.contrib.sessions.middleware.SessionMiddleware",
	"django.middleware.common.CommonMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	"django.contrib.messages.middleware.MessageMiddleware",
	"django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
	{
		"BACKEND": "django.template.backends.django.DjangoTemplates",
		"DIRS": [BASE_DIR / "templates"],
		"APP_DIRS": True,
		"OPTIONS": {
			"context_processors": [
				"django.template.context_processors.debug",
				"django.template.context_processors.request",
				"django.contrib.auth.context_processors.auth",
				"django.contrib.messages.context_processors.messages",
			],
		},
	}
]

DATABASES = {
	"default": {
		"ENGINE": env("DATABASE_ENGINE", default="django.db.backends.sqlite3"),
		"NAME": env("DATABASE_NAME", default=str(BASE_DIR / "db.sqlite3")),
		"USER": env("DATABASE_USER", default=""),
		"PASSWORD": env("DATABASE_PASSWORD", default=""),
		"HOST": env("DATABASE_HOST", default=""),
		"PORT": env("DATABASE_PORT", default=""),
	}
}

AUTH_PASSWORD_VALIDATORS = [
	{"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
	{"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
	{"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
	{"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = env("LANGUAGE_CODE", default="en-us")
TIME_ZONE = env("TIME_ZONE", default="Africa/Nairobi")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@bimagrid.io")

REST_FRAMEWORK = {
	"DEFAULT_RENDERER_CLASSES": [
		"rest_framework.renderers.JSONRenderer",
	],
	"DEFAULT_PARSER_CLASSES": [
		"rest_framework.parsers.JSONParser",
		"rest_framework.parsers.FormParser",
		"rest_framework.parsers.MultiPartParser",
	],
	"DEFAULT_AUTHENTICATION_CLASSES": [
		"rest_framework.authentication.SessionAuthentication",
		"apps.accounts.authentication.BearerTokenAuthentication",
		"rest_framework.authentication.TokenAuthentication",
	],
	"DEFAULT_PERMISSION_CLASSES": [
		"rest_framework.permissions.IsAuthenticatedOrReadOnly",
	],
	"DEFAULT_FILTER_BACKENDS": [
		"django_filters.rest_framework.DjangoFilterBackend",
		"rest_framework.filters.SearchFilter",
		"rest_framework.filters.OrderingFilter",
	],
}

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://redis:6379/1")
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=not DEBUG)
X_FRAME_OPTIONS = "DENY"
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

BIMAGRID_VERSION = env("BIMAGRID_VERSION", default="1.0.0")

# External integrations — mock fallbacks when credentials are absent
MPESA_CONSUMER_KEY = env("MPESA_CONSUMER_KEY", default="")
MPESA_CONSUMER_SECRET = env("MPESA_CONSUMER_SECRET", default="")
MPESA_SHORTCODE = env("MPESA_SHORTCODE", default="174379")
MPESA_PASSKEY = env("MPESA_PASSKEY", default="")
MPESA_INITIATOR_NAME = env("MPESA_INITIATOR_NAME", default="BimaGridAdmin")
MPESA_SECURITY_CREDENTIAL = env("MPESA_SECURITY_CREDENTIAL", default="")
MPESA_B2C_SHORTCODE = env("MPESA_B2C_SHORTCODE", default="600123")
MPESA_CALLBACK_BASE_URL = env("MPESA_CALLBACK_BASE_URL", default="http://localhost:8000")
MPESA_ENVIRONMENT = env("MPESA_ENVIRONMENT", default="sandbox")
MPESA_USE_MOCK = env.bool("MPESA_USE_MOCK", default=not bool(MPESA_CONSUMER_KEY))

AFRICASTALKING_USERNAME = env("AFRICASTALKING_USERNAME", default="sandbox")
AFRICASTALKING_API_KEY = env("AFRICASTALKING_API_KEY", default="")
AFRICASTALKING_SENDER_ID = env("AFRICASTALKING_SENDER_ID", default="BimaGrid")
AFRICASTALKING_USE_MOCK = env.bool("AFRICASTALKING_USE_MOCK", default=not bool(AFRICASTALKING_API_KEY))

# Standalone USSD service (optional proxy target)
USSD_SERVICE_URL = env("USSD_SERVICE_URL", default="")
USSD_SERVICE_TIMEOUT = env.float("USSD_SERVICE_TIMEOUT", default=10.0)
USSD_INTERNAL_API_KEY = env("USSD_INTERNAL_API_KEY", default="bimagrid-ussd-internal-dev-key")

OPENEO_BACKEND_URL = env("OPENEO_BACKEND_URL", default="https://earthengine.openeo.org")
OPENEO_USERNAME = env("OPENEO_USERNAME", default="")
OPENEO_PASSWORD = env("OPENEO_PASSWORD", default="")
OPENEO_USE_MOCK = env.bool("OPENEO_USE_MOCK", default=not bool(OPENEO_USERNAME))

IPRS_API_URL = env("IPRS_API_URL", default="https://iprs.go.ke/api/v1")
IPRS_API_KEY = env("IPRS_API_KEY", default="")
IPRS_USE_MOCK = env.bool("IPRS_USE_MOCK", default=not bool(IPRS_API_KEY))

ARDHISASA_API_URL = env("ARDHISASA_API_URL", default="https://ardhisasa.lands.go.ke/api/v1")
ARDHISASA_CLIENT_ID = env("ARDHISASA_CLIENT_ID", default="")
ARDHISASA_CLIENT_SECRET = env("ARDHISASA_CLIENT_SECRET", default="")
ARDHISASA_USE_MOCK = env.bool("ARDHISASA_USE_MOCK", default=not bool(ARDHISASA_CLIENT_ID))

BLOCKCHAIN_RPC_URL = env("BLOCKCHAIN_RPC_URL", default="http://localhost:8545")
ORACLE_SIGNATURE_VERIFY = env.bool("ORACLE_SIGNATURE_VERIFY", default=False)
ORACLE_AUTHORIZED_KEYS = env.list("ORACLE_AUTHORIZED_KEYS", default=[])

H3_DEFAULT_RESOLUTION = env.int("H3_DEFAULT_RESOLUTION", default=9)

RATE_LIMIT_REQUESTS = env.int("RATE_LIMIT_REQUESTS", default=120)
RATE_LIMIT_WINDOW_SECONDS = env.int("RATE_LIMIT_WINDOW_SECONDS", default=60)

LOGGING = {
	"version": 1,
	"disable_existing_loggers": False,
	"formatters": {
		"verbose": {
			"format": "{asctime} {levelname} {name} {message}",
			"style": "{",
		}
	},
	"handlers": {
		"console": {
			"class": "logging.StreamHandler",
			"formatter": "verbose",
		}
	},
	"root": {
		"handlers": ["console"],
		"level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
	},
}

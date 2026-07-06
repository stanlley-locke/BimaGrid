"""Django settings for the BimaGrid standalone USSD service."""

from __future__ import annotations

import os
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parents[2]
env = environ.Env(
	DEBUG=(bool, False),
	SESSION_TTL=(int, 180),
	RATE_LIMIT_REQUESTS=(int, 100),
	RATE_LIMIT_WINDOW_SECONDS=(int, 60),
)
environ.Env.read_env(BASE_DIR.parent / ".env")
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("USSD_SECRET_KEY", default="ussd-dev-secret-key-change-in-production")
DEBUG = env.bool("USSD_DEBUG", default=True)
ALLOWED_HOSTS = env.list("USSD_ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "0.0.0.0"])

INSTALLED_APPS = [
	"django.contrib.contenttypes",
	"django.contrib.auth",
	"src.gateway.apps.GatewayConfig",
]

MIDDLEWARE = [
	"django.middleware.security.SecurityMiddleware",
	"src.gateway.middleware.RequestLoggingMiddleware",
	"src.gateway.middleware.RateLimitMiddleware",
]

ROOT_URLCONF = "src.config.urls"
WSGI_APPLICATION = "src.config.wsgi.application"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "ussd.sqlite3"}}

USE_TZ = True
TIME_ZONE = env("TIME_ZONE", default="Africa/Nairobi")
LANGUAGE_CODE = "en-us"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Africa's Talking
AFRICASTALKING_USERNAME = env("AFRICASTALKING_USERNAME", default="sandbox")
AFRICASTALKING_API_KEY = env("AFRICASTALKING_API_KEY", default="")
AFRICASTALKING_VERIFY_SIGNATURE = env.bool("AFRICASTALKING_VERIFY_SIGNATURE", default=False)

# Backend integration
BACKEND_URL = env("BACKEND_URL", default="http://localhost:8000").rstrip("/")
BACKEND_API_KEY = env(
	"BACKEND_API_KEY",
	default=env("USSD_INTERNAL_API_KEY", default="bimagrid-ussd-internal-dev-key"),
)
BACKEND_TIMEOUT_SECONDS = env.float("BACKEND_TIMEOUT_SECONDS", default=10.0)

# Session state
REDIS_URL = env("REDIS_URL", default="")
SESSION_TTL = env.int("SESSION_TTL", default=180)
USE_IN_MEMORY_SESSIONS = env.bool("USE_IN_MEMORY_SESSIONS", default=not bool(REDIS_URL))

# Rate limiting
RATE_LIMIT_REQUESTS = env.int("RATE_LIMIT_REQUESTS", default=100)
RATE_LIMIT_WINDOW_SECONDS = env.int("RATE_LIMIT_WINDOW_SECONDS", default=60)

USSD_VERSION = env("USSD_VERSION", default="1.0.0")

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
		"level": os.getenv("USSD_LOG_LEVEL", "INFO"),
	},
}

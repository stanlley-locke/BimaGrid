"""Testing Django settings."""

from .base import *  # noqa: F401,F403

DEBUG = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
MPESA_USE_MOCK = True
AFRICASTALKING_USE_MOCK = True
OPENEO_USE_MOCK = True
IPRS_USE_MOCK = True
ARDHISASA_USE_MOCK = True
ORACLE_SIGNATURE_VERIFY = False
RATE_LIMIT_REQUESTS = 1000
USSD_INTERNAL_API_KEY = ""

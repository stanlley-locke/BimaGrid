"""WSGI entry point for the USSD service."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.config.settings")

application = get_wsgi_application()

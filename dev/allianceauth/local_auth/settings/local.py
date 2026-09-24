import os
from pathlib import Path

from allianceauth.project_template.project_name.settings.base import *  # noqa: F403, F401

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ROOT_URLCONF = "local_auth.urls"
WSGI_APPLICATION = "local_auth.wsgi.application"
SECRET_KEY = os.getenv("AA_SECRET_KEY", "local-development-only-secret-key")

SITE_NAME = "Wiki.js Plugin Development"
SITE_URL = "http://localhost:8000"
CSRF_TRUSTED_ORIGINS = [SITE_URL]
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
DEBUG = True

STATIC_ROOT = PROJECT_ROOT / "static"

INSTALLED_APPS += ["wikijs"]  # noqa: F405

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": PROJECT_ROOT / "alliance_auth.sqlite3",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("AA_REDIS_URL", "redis://127.0.0.1:6379/1"),
    }
}

BROKER_URL = os.getenv("AA_REDIS_URL", "redis://127.0.0.1:6379/0")
CELERY_BROKER_URL = BROKER_URL
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

ESI_SSO_CLIENT_ID = os.getenv("AA_ESI_CLIENT_ID", "local-development")
ESI_SSO_CLIENT_SECRET = os.getenv("AA_ESI_CLIENT_SECRET", "local-development")
ESI_SSO_CALLBACK_URL = f"{SITE_URL}/sso/callback"
ESI_USER_CONTACT_EMAIL = os.getenv("AA_ESI_CONTACT_EMAIL", "developer@example.invalid")

REGISTRATION_VERIFY_EMAIL = False
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "allianceauth@example.invalid"

WIKIJS_URL = os.getenv("WIKIJS_URL", "http://localhost:3000")
WIKIJS_API_URL = os.getenv("WIKIJS_API_URL", WIKIJS_URL)
WIKIJS_API_KEY = os.getenv("WIKIJS_API_KEY", "")
WIKIJS_AADISCORDBOT_INTEGRATION = False

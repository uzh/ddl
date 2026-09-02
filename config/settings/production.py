import os

from csp.constants import NONE, SELF, UNSAFE_INLINE

from .base import *  # noqa: F403
from .base import BASE_DIR

# Accepts a comma- and/or whitespace-separated list, e.g. "a.example b.example".
ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].replace(",", " ").split()

SITE_ID = 1


# DEBUG
# ------------------------------------------------------------------------------
DEBUG = False


# SECURITY SETTINGS
# ------------------------------------------------------------------------------
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

# HSTS. Preload is intentionally not set: datadonation.uzh.ch cannot be added to
# the browser preload list independently of uzh.ch.
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Content Security Policy (django-csp).
# Report-only for now: browsers log violations but nothing is blocked. Watch the
# console on the public site and the Wagtail/Django admin, then tighten (drop
# 'unsafe-inline' from script-src once the inline Matomo bootstrap in
# ddl/templates/ddl/base.html uses request.csp_nonce) and promote to
# CONTENT_SECURITY_POLICY.
MATOMO_HOST = "https://webstats.uzh.ch"
CONTENT_SECURITY_POLICY_REPORT_ONLY = {
    "DIRECTIVES": {
        "default-src": [SELF],
        "script-src": [SELF, UNSAFE_INLINE, MATOMO_HOST],
        "style-src": [SELF, UNSAFE_INLINE],
        "img-src": [SELF, "data:", MATOMO_HOST],
        "font-src": [SELF],
        "connect-src": [SELF, MATOMO_HOST],
        "frame-src": [SELF],
        "frame-ancestors": [NONE],
        "base-uri": [SELF],
        "form-action": [SELF],
        "object-src": [NONE],
    },
}

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"


# EMAIL (authenticated SMTP)
# ------------------------------------------------------------------------------
# Django's default SMTP backend is used. Errors are mailed to ADMINS via the
# mail_admins logging handler below; From address is SERVER_EMAIL (see base.py).
EMAIL_HOST = os.environ["EMAIL_HOST"]
EMAIL_PORT = int(os.environ.get("EMAIL_PORT") or 587)
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").lower() == "true"
EMAIL_TIMEOUT = 10


# LOGGING
# ------------------------------------------------------------------------------
LOG_DIR = BASE_DIR / "logs"
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "filters": {"require_debug_false": {"class": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "datadlab.log",
            "maxBytes": 1024 * 1024 * 15,
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "errors.log",
            "maxBytes": 1024 * 1024 * 15,
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": False,
            "filters": ["require_debug_false"],
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "error_file", "mail_admins"],
            "propagate": True,
            "level": "INFO",
        },
        "": {"handlers": ["file", "error_file"], "level": "WARNING"},
    },
}


# DATABASE
# ------------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": os.environ["DJANGO_DB_HOST"],
        "PORT": "",
        "NAME": os.environ["DJANGO_DB_NAME"],
        "USER": os.environ["DJANGO_DB_USER"],
        "PASSWORD": os.environ["DJANGO_DB_PW"],
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

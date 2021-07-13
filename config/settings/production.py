from .base import *

ALLOWED_HOSTS = [
    'datadonation.uzh.ch',
    'www.datadonation.uzh.ch',
    'data-donation.uzh.ch',
    'www.data-donation.uzh.ch',
    'idikmzdatad01.uzh.ch',
]

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = False

SITE_ID = 1

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

SECURE_HSTS_SECONDS = 3600
SECURE_SSL_REDIRECT = True

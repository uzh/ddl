import os
import ddm.core
from .base import *


ALLOWED_HOSTS = []

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = True

SITE_ID = 1

# DATABASE
# ------------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'datadlab.sqlite',
    }
}

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': 'core/vue/',
        'STATS_FILE': os.path.join(os.path.dirname(ddm.core.__file__), 'static/ddm_core/vue/webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
    },
    'GPT': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': 'gpt/vue/',
        'STATS_FILE': os.path.join(BASE_DIR, 'gpt', 'static', 'gpt', 'vue', 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
    }
}

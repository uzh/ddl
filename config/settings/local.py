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
    'DDM_UPLOADER': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': 'ddm_core/frontend/uploader/',
        'STATS_FILE': os.path.join(
            os.path.dirname(ddm.core.__file__),
            'static/ddm_core/frontend/uploader/webpack-stats.json'
        ),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    },
    'DDM_QUESTIONNAIRE': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': 'ddm_core/frontend/questionnaire/',
        'STATS_FILE': os.path.join(
            os.path.dirname(ddm.core.__file__),
            'static/ddm_core/frontend/questionnaire/webpack-stats.json'
        ),
        'POLL_INTERVAL': 0.1,
        'TIMEOUT': None,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map']
    },
    'GPT': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': 'gpt/vue/',
        'STATS_FILE': os.path.join(BASE_DIR, 'gpt', 'static', 'gpt', 'vue', 'webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
    }
}

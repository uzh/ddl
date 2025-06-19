import os

from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# APPLICATION DEFINITIONS
# ------------------------------------------------------------------------------
SECRET_KEY = os.environ['DJANGO_SECRET']

INSTALLED_APPS = [
    'ddl.apps.DdlConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'mozilla_django_oidc',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'ddm',
    'ddm.apis',
    'ddm.auth',
    'ddm.logging',
    'ddm.questionnaire',
    'ddm.datadonation',
    'ddm.participation',
    'ddm.projects',
    'ddm.core',
    'gpt',
    'reports',
    'django_ckeditor_5',
    'webpack_loader',
    'rest_framework',
    'rest_framework.authtoken',
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.locales',
    'wagtail.contrib.simple_translation',
    'wagtail',
    'modelcluster',
    'taggit',
    'cookie_consent',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    'ddl.middleware.ConditionalSessionRefreshMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'ddl.auth.DDLOIDCAuthenticationBackend',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'ddm.core.context_processors.add_ddm_version',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# USER AUTHORIZATION AND PASSWORD VALIDATION
# ------------------------------------------------------------------------------
AUTH_USER_MODEL = "ddl.User"

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# INTERNATIONALIZATION
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'en'
TIME_ZONE = 'Europe/Zurich'
USE_I18N = True
USE_L10N = True
USE_TZ = True
WAGTAIL_I18N_ENABLED = True
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ('en', "English"),
    ('de', "Deutsch")
]


# STATIC FILES
# ------------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles/')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')


# DEFAULT PRIMARY KEY FIELD TYPE
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

X_FRAME_OPTIONS = 'SAMEORIGIN'


# DJANGO-FILER
# ------------------------------------------------------------------------------
THUMBNAIL_HIGH_RESOLUTION = True

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters'
)


# WAGTAIL
# ------------------------------------------------------------------------------
WAGTAIL_SITE_NAME = 'Data Donation Lab'
WAGTAILADMIN_BASE_URL = os.getenv('WAGTAILADMIN_BASE_URL', 'https://datadonation.uzh.ch')


# OIDC Authentication (mozilla_django_oidc)
# ------------------------------------------------------------------------------
OIDC_RP_SIGN_ALGO = 'RS256'
OIDC_OP_JWKS_ENDPOINT = 'https://login.eduid.ch/idp/profile/oidc/keyset'
OIDC_RP_CLIENT_ID = os.getenv('OIDC_RP_CLIENT_ID', None)
OIDC_RP_CLIENT_SECRET = os.getenv('OIDC_RP_CLIENT_SECRET', None)

# Stage Settings
OIDC_OP_AUTHORIZATION_ENDPOINT = os.getenv('OIDC_OP_AUTHORIZATION_ENDPOINT', 'https://login.eduid.ch/idp/profile/oidc/authorize')
OIDC_OP_TOKEN_ENDPOINT = os.getenv('OIDC_OP_TOKEN_ENDPOINT', 'https://login.eduid.ch/idp/profile/oidc/token')
OIDC_OP_USER_ENDPOINT = os.getenv('OIDC_OP_USER_ENDPOINT', 'https://login.eduid.ch/idp/profile/oidc/userinfo')

OIDC_RP_SCOPES = 'openid email swissEduIDAssociatedMail'

# Redirect targets:
LOGIN_REDIRECT_URL = '/ddm/projects/'
LOGOUT_REDIRECT_URL = '/ddm/login/'

OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = 60 * 60 * 4


# DJANGO-DDM
# ------------------------------------------------------------------------------
WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': 'ddm_core/vue/',
        'STATS_FILE': os.path.join(STATIC_ROOT, 'ddm_core/vue/webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
    },
    'GPT': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': 'gpt/vue/',
        'STATS_FILE': os.path.join(STATIC_ROOT, 'gpt/vue/webpack-stats.json'),
        'POLL_INTERVAL': 0.1,
        'IGNORE': [r'.+\.hot-update.js', r'.+\.map'],
    }
}
DDM_SETTINGS = {
    'EMAIL_PERMISSION_CHECK':  r'.*(\.|@)uzh\.ch$',
}

DDM_DEFAULT_HEADER_IMG_LEFT = '/static/ddl/img/logos/ddl/ddl_logo_black.svg'
DDM_DEFAULT_HEADER_IMG_RIGHT = '/static/ddl/img/logos/external/uzh_logo_d_pos.svg'


# CKEditor
# ------------------------------------------------------------------------------
CKEDITOR_5_FILE_UPLOAD_PERMISSION = 'authenticated'
CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True
CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'pdf', 'png', 'mp4']

ATTRIBUTES_TO_ALLOW = {
    'href': True,
    'target': True,
    'rel': True,
    'class': True,
    'aria-label': True,
    'data-*': True,
    'id': True,
    'type': True,
    'data-bs-toggle': True,
    'data-bs-target': True,
    'data-bs-parent': True,
    'aria-expanded': True,
    'aria-controls': True,
    'aria-labelledby': True,
}

CKEDITOR_5_CONFIGS = {
    'ddm_ckeditor':  {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': [
            'heading', '|',
            'alignment', 'outdent', 'indent', '|',
            'bold', 'italic', 'underline', 'link', 'highlight', '|',
            {
                'label': 'Fonts',
                'icon': 'text',
                'items': ['fontSize', 'fontFamily', 'fontColor']
            }, '|',
            'bulletedList', 'numberedList', 'insertTable', 'blockQuote', 'code', 'removeFormat', '|',
            'insertImage', 'fileUpload', 'mediaEmbed', '|',
            'sourceEditing'
        ],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                        'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignRight',
                'alignCenter',
            ]
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells',
                               'tableProperties', 'tableCellProperties'],
        },
        'heading': {
            'options': [
                { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
                { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
                { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
                { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
            ]
        },
        'htmlSupport': {
            'allow': [
                {
                    'name': 'video',
                    'attributes': {
                        'height': True,
                        'width': True,
                        'controls': True,
                    },
                    'styles': True
                },
                {
                    'name': 'p',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'span',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'div',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'a',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'table',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'td',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'th',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'button',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'h1',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'h2',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
                {
                    'name': 'style',
                    'attributes': ATTRIBUTES_TO_ALLOW
                },
            ],
            'disallow': []
        },
        'wordCount': {
            'displayCharacters': False,
            'displayWords': False,
        }
    }
}


# Reports
# ------------------------------------------------------------------------------
# Search Report
SEARCH_PROJECT_PK = os.getenv('SEARCH_PROJECT_PK', None)
SEARCH_API_KEY = os.getenv('SEARCH_API_KEY', None)

# Digital Meal Report
DIGITALMEAL_PROJECT_PK = os.getenv('DIGITALMEAL_PROJECT_PK', None)
DIGITALMEAL_API_KEY = os.getenv('DIGITALMEAL_API_KEY', None)

# ChatGPT Report
CHATGPT_PROJECT_PK = os.getenv('CHATGPT_PROJECT_PK', None)
CHATGPT_API_KEY = os.getenv('CHATGPT_API_KEY', None)

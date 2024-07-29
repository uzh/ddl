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
    'ckeditor',
    'ckeditor_uploader',
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
    'reports'
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
    'mozilla_django_oidc.middleware.SessionRefresh'
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
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
                'ddm.context_processors.add_ddm_version',
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
WAGTAILSIMPLETRANSLATION_SYNC_PAGE_TREE = True

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

# Redirect targets:
LOGIN_REDIRECT_URL = '/ddm/projects/'
LOGOUT_REDIRECT_URL = '/ddm/login/'


# DJANGO-DDM
# ------------------------------------------------------------------------------
WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': True,
        'BUNDLE_DIR_NAME': 'ddm/vue/',
        'STATS_FILE': os.path.join(STATIC_ROOT, 'ddm/vue/webpack-stats.json'),
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
CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_UPLOAD_PATH = 'uploads/'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': 300,
    },
}

# Reports
# ------------------------------------------------------------------------------
POLITICS_KEY = os.getenv('POLITICS_KEY', None)

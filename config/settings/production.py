from .base import *
import os


ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split()

SITE_ID = 1


# DEBUG
# ------------------------------------------------------------------------------
DEBUG = False


# SECURITY SETTINGS
# ------------------------------------------------------------------------------
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# HSTS
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# TODO: CSP (https://realpython.com/django-nginx-gunicorn/#adding-a-content-security-policy-csp-header)
# MIDDLEWARE += ['csp.middleware.CSPMiddleware']
# CSP_STYLE_SRC = ["'self'"]

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'


# LOGGING
# ------------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'datadlab.log'),
            'maxBytes': 1024*1024*15,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}


# DATABASE
# ------------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.environ['DJANGO_DB_HOST'],
        'PORT': '',
        'NAME': os.environ['DJANGO_DB_NAME'],
        'USER': os.environ['DJANGO_DB_USER'],
        'PASSWORD': os.environ['DJANGO_DB_PW'],
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}


# CKEDITOR Settings
# ------------------------------------------------------------------------------
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
            ],
            'disallow': []
        },
        'wordCount': {
            'displayCharacters': False,
            'displayWords': False,
        }
    }
}

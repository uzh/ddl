from .base import *

import os

SECRET_KEY = os.environ['DJANGO_SECRET']

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = False

# DATABASE
# ------------------------------------------------------------------------------
DATABASES['default']['NAME'] = os.environ['DJANGO_DB_NAME']
DATABASES['default']['USER'] = os.environ['DJANGO_DB_USER']
DATABASES['default']['PASSWORD'] = os.environ['DJANGO_DB_PW']

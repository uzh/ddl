from .base import *

SECRET_KEY = 'django-insecure-j^a2aa+k8%_#h-#20!2v#7v6i2($_h#$!372l%!1qv2@^62rsf'

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = True

# DATABASE
# ------------------------------------------------------------------------------
DATABASES['default']['NAME'] = 'datadlab'
DATABASES['default']['USER'] = 'postgres'
DATABASES['default']['PASSWORD'] = 'password'

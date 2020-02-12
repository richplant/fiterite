from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1$$e7-z52tb+0#26qbgu_b$7)flby%g1l39a92ek=nyc=0bfy$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

try:
    from .local import *
except ImportError:
    pass


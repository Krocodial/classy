"""
Django settings for this project.

Generated by 'django-admin startproject' using Django 1.11.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
from keycloak.realm import KeycloakRealm
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# The SECRET_KEY is provided via an environment variable in OpenShift
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    # safe value used for development when DJANGO_SECRET_KEY might not be set
    '9e4@&tw46$l31)zrqe3wi+-slqm(ruvz&se0^%9#6(_w3ui!c0'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', False)
BYPASS_AUTH = os.getenv('BYPASS_AUTH', False)
PRES = os.getenv('PRES', False)
ALLOWED_HOSTS = ['*']
AUTH_USER_MODEL = 'auth.User'

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', True)
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', True)
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
#SECURE_HSTS_SECONDS = 600
#SECURE_HSTS_INCLUDE_SUBDOMAINS = True
#SECURE_HSTS_PRELOAD = True
#SECURE_SSL_REDIRECT = True
X_FRAME_OPTIONS = 'DENY'
#SESSION_COOKIE_AGE = 300 
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
USE_X_FORWARDED_HOST = True

SSO_REALM = KeycloakRealm(server_url=os.getenv('SSO_SERVER'), realm_name=os.getenv('SSO_REALM'))
OIDC_CLIENT = SSO_REALM.open_id_connect(client_id=os.getenv('SSO_CLIENT_ID'), 
                                        client_secret=os.getenv('SSO_CLIENT_SECRET'))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'classy.apps.ClassyConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'classy.middleware.authentication.authentication_middleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'classy/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'ratelimit_cache_table',
    }
}


from . import database

DATABASES = {
    'default': database.config()
}

CONCURRENCY = database.CONCURRENCY

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Canada/Pacific'

USE_I18N = True

USE_L10N = True

USE_TZ = True



LOGIN_URL = 'classy:index'
LOGIN_REDIRECT_URL = 'classy:home'

FILE_UPLOAD_PERMISSIONS = 0o600

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'conf/html/')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


"""
Django settings for eegi project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Local configuration
from local_settings import (
    DEBUG, SECRET_KEY, LOCKDOWN_PASSWORDS, DATABASES, MATERIALS_DIR,
    BASE_URL_IMG, BASE_URL_THUMBNAIL, BASE_URL_DEVSTAR)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'website',
    'dbmigration',
    'worms',
    'clones',
    'library',
    'experiments',
]

if DEBUG:
    # INSTALLED_APPS.append('debug_toolbar')
    pass

else:
    # Must be listed after website, so the lockdown custom template
    # (which is inside the website app) has precedence.
    INSTALLED_APPS.append('lockdown')

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'lockdown.middleware.LockdownMiddleware',
)

ROOT_URLCONF = 'eegi.urls'

WSGI_APPLICATION = 'eegi.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

SHORT_DATE_FORMAT = 'Y-m-d'

USE_I18N = True

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = 'staticfiles'


# For request objects in templates

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)


# Login

LOGIN_URL = 'login_url'


# Site password protection

LOCKDOWN_FORM = 'lockdown.forms.LockdownForm'

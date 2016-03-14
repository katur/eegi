"""
Django settings for the eegi project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Import local configuration

from localsettings import (
    DEBUG, SECRET_KEY, LOCKDOWN_PASSWORDS, DATABASES, STATIC_ROOT,
    BASE_DIR_DEVSTAR_OUTPUT, BASE_DIR_IMAGE_CATEGORIES,
    BASE_URL_IMG, BASE_URL_THUMBNAIL, BASE_URL_DEVSTAR,
    GOOGLE_ANALYTICS_ID, GOOGLE_API_KEY,
    BATCH_DATA_ENTRY_GDOC_NAME, BATCH_DATA_ENTRY_GDOC_URL)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Security

ALLOWED_HOSTS = ['*']


# Administration

ADMINS = [('Katherine Erickson', 'katherine.erickson@gmail.com')]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'jquery',

    'website',
    'worms',
    'clones',
    'library',
    'experiments',

    # Must be listed after website
    'lockdown',
]

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

USE_I18N = True

USE_L10N = False

USE_TZ = True

SHORT_DATE_FORMAT = 'Y-m-d'


# Static files
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'


# Templates
# (Customized to provide request object in templates)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,

        # Needed so overridden admin templates take precedence
        'DIRS': [BASE_DIR + '/website/templates/'],

        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'eegi.context_processors.google_analytics',
            ],
        },
    },
]


# Login

LOGIN_URL = 'login_url'
LOGIN_REDIRECT_URL = '/'


# Site password protection

LOCKDOWN_FORM = 'lockdown.forms.LockdownForm'

"""
Django settings for delivery24 project.

Generated by 'django-admin startproject' using Django 3.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import datetime

from django.urls import reverse_lazy

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

SECRET_KEY = os.getenv('DELIVERY24_DJANGO_SECRET_KEY')
DB_NAME = os.getenv('DELIVERY24_DB_NAME')
DB_USER = os.getenv('DELIVERY24_DB_USER')
DB_PASS = os.getenv('DELIVERY24_DB_PASS')
DB_HOST = os.getenv('DELIVERY24_DB_HOST')
DB_PORT = os.getenv('DELIVERY24_DB_PORT')
GMAIL_USER = os.getenv('DELIVERY24_GMAIL_USER')
GMAIL_PASS = os.getenv('DELIVERY24_GMAIL_PASS')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []  # 'localhost', '127.0.0.1', '[::1]'


# Application definition

INSTALLED_APPS = [
    'core',
    'accounts',
    'phonenumber_field',
    'axes',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # AxesMiddleware should be the last middleware in the MIDDLEWARE list.
    # It only formats user lockout messages and renders Axes lockout responses
    # on failed user authentication attempts from login views.
    # If you do not want Axes to override the authentication response
    # you can skip installing the middleware and use your own views.
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'delivery24.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'delivery24.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASS,
        'HOST': 'localhost',
        'PORT': '',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]
LANGUAGE_CODE = 'en-us'
LANGUAGES = [
    ('en-us', 'English'),
    ('ru', 'Russian'),
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

AUTH_USER_MODEL = 'accounts.User'

LOGIN_REDIRECT_URL = reverse_lazy('accounts:profile')
LOGOUT_REDIRECT_URL = reverse_lazy('core:index')
LOGIN_URL = reverse_lazy('accounts:login')
LOGOUT_URL = reverse_lazy('accounts:logout')

PASSWORD_RESET_TIMEOUT_DAYS = 1

# Email send
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = GMAIL_USER
    EMAIL_HOST_PASSWORD = GMAIL_PASS
    EMAIL_PORT = 587
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    # Django ModelBackend is the default authentication backend.
    'django.contrib.auth.backends.ModelBackend',
]
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 6
AXES_COOLOFF_TIME = datetime.timedelta(minutes=1)
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_LOCKOUT_TEMPLATE = 'accounts/account_lockout.html'
AXES_LOCKOUT_URL = reverse_lazy('core:index')

PHONENUMBER_DB_FORMAT = 'E164'
PHONENUMBER_DEFAULT_REGION = 'EE'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(name)-12s: %(message)s'  # "rich": {"datefmt": "[%X]"}
        },
        'file': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'rich.logging.RichHandler',
            'formatter': 'console'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'file',
            'filename': 'debug.log',
            'maxBytes': 1048576,  # 1*1024*1024 bytes (1MB)
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            # 'propagate': True
        }
    }
}
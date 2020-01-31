# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright 2019, GeoSolutions SAS.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################

import os
import dj_database_url
from .utils import EnvUtil
from datetime import timedelta
from django.utils.translation import gettext_lazy as _


# ############################################################################ #
# default variables
# ############################################################################ #
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir))))
REACT_APP_DIR = os.path.join(BASE_DIR, 'serapide_client') # serapide-client

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = EnvUtil.get_env_var('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = EnvUtil.get_env_var('DJANGO_DEBUG', type=bool, default=False)

ROOT_URLCONF = 'base.urls'
WSGI_APPLICATION = 'base.wsgi.application'

HOSTNAME = EnvUtil.get_env_var('HOSTNAME', default='localhost')
PROJECT_NAME = EnvUtil.get_env_var('PROJECT_NAME', default='strt')
SITE_ID = EnvUtil.get_env_var('DJANGO_SITE_ID', type=int, default=1)
SITE_URL = EnvUtil.get_env_var('DJANGO_PUBLIC_URL', default='http://%s:8000' % HOSTNAME)
SITE_NAME = EnvUtil.get_env_var('DJANGO_SITE_NAME', default='Statuto Territorio RT')

ALLOWED_HOSTS = EnvUtil.get_env_var('DJANGO_ALLOWED_HOSTS', type=list, default=[HOSTNAME, ], separator=' ')

LOGIN_URL = EnvUtil.get_env_var('LOGIN_URL', default='/private-area/')
LOGOUT_REDIRECT_URL = EnvUtil.get_env_var('LOGOUT_REDIRECT_URL', default='/')

LOGIN_FRONTEND_URL = EnvUtil.get_env_var('LOGIN_FRONTEND_URL', default='users/login')
LOGIN_FRONTEND_TEMPLATE = EnvUtil.get_env_var('LOGIN_FRONTEND_TEMPLATE', default='users/login.html')

# ############################################################################ #
# Wagtail settings
# ############################################################################ #
WAGTAIL_SITE_NAME = SITE_NAME
WAGTAIL_FRONTEND_LOGIN_URL = LOGIN_FRONTEND_URL
WAGTAIL_FRONTEND_LOGIN_TEMPLATE = LOGIN_FRONTEND_TEMPLATE

# ############################################################################ #
# notifications backends
# ############################################################################ #
DEFAULT_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Define email service on GeoNode
EMAIL_ENABLE = EnvUtil.get_env_var('EMAIL_ENABLE', type=bool, default=False)
EMAIL_BACKEND = EnvUtil.get_env_var('DJANGO_EMAIL_BACKEND', default=DEFAULT_EMAIL_BACKEND)
EMAIL_HOST = EnvUtil.get_env_var("DJANGO_EMAIL_HOST", default=HOSTNAME)
EMAIL_PORT = EnvUtil.get_env_var("DJANGO_EMAIL_PORT", type=int, default=25)
EMAIL_HOST_USER = EnvUtil.get_env_var("DJANGO_EMAIL_HOST_USER", default='')
EMAIL_HOST_PASSWORD = EnvUtil.get_env_var("DJANGO_EMAIL_HOST_PASSWORD", default='')
EMAIL_USE_TLS = EnvUtil.get_env_var('DJANGO_EMAIL_USE_TLS', type=bool, default=False)
DEFAULT_FROM_EMAIL = EnvUtil.get_env_var("DEFAULT_FROM_EMAIL", default='%s <no-reply@%s>' % (SITE_NAME, HOSTNAME))

# notification settings
NOTIFICATIONS_ENABLED = EnvUtil.get_env_var('NOTIFICATIONS_ENABLED', type=bool, default=True)
NOTIFICATIONS_MODULE = EnvUtil.get_env_var("NOTIFICATIONS_MODULE", default='pinax.notifications')

if EMAIL_ENABLE:
    # (media_id, backend, spam_sensitivity)
    PINAX_NOTIFICATIONS_BACKENDS = [
        # ('email', 'pinax.notifications.backends.email.EmailBackend', 0),
        ('email', 'serapide_core.notifications_backends.EmailBackend', 0),
    ]
PINAX_NOTIFICATIONS_HOOKSET = "pinax.notifications.hooks.DefaultHookSet"

# Queue non-blocking notifications.
PINAX_NOTIFICATIONS_QUEUE_ALL = False
PINAX_NOTIFICATIONS_LOCK_WAIT_TIMEOUT = -1

# ############################################################################ #
# django modules
# ############################################################################ #
# Application definition
INSTALLED_APPS = [
    # StatutoTerritorioRT apps
    'base',
    'strt_portal',
    'strt_users',
    # Django apps
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'django_celery_beat',
    'django_extensions',
    # Pinax apps
    'fontawesome',
    'bootstrapform',
    'pinax.messages',
    'pinax.templates',
    'pinax.notifications',
    # Wagtail apps
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
    'wagtail.core',
    'modelcluster',
    'taggit',
    # Crispy forms
    'crispy_forms',
    # Rules
    'rules.apps.AutodiscoverRulesConfig',
    # DRF
    'rest_framework',
    # TEST
    'strt_tests',
    # This will also make the `graphql_schema` management command available
    'graphene_django',

    # Install the ingredients app
    'serapide_core',
    'serapide_core.modello',
    'serapide_core.api',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),
            os.path.join(REACT_APP_DIR, 'build'),
        ],
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

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    'default': dj_database_url.parse(
        EnvUtil.get_env_var('DJANGO_DATABASE_URL',
                            default="sqlite:///{}".format(
                                os.path.join(BASE_DIR, 'db.sqlite3')))
    )
}

#AUTH_USER_MODEL = 'strt_users.AppUser'
AUTH_USER_MODEL = 'strt_users.Utente'

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = (
    'strt_users.backends.StrtPortalAuthentication',
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

TOKEN_EXPIRE_DAYS = 60

RESPONSABILE_ISIDE_CODE = EnvUtil.get_env_var('RESPONSABILE_ISIDE_CODE', default='RI')
RUP_CODE = EnvUtil.get_env_var('RUP_CODE', default='RUP')

TEMP_USER_CODE = EnvUtil.get_env_var('TEMP_USER_CODE', default='TMP')
READ_ONLY_USER_CODE = EnvUtil.get_env_var('READ_ONLY_USER_CODE', default='RO')
OPERATOR_USER_CODE = EnvUtil.get_env_var('OPERATOR_USER_CODE', default='OP')

DEFAULT_MUNICIPALITY = EnvUtil.get_env_var('DEFAULT_MUNICIPALITY', default='Firenze')

VERIFICA_VAS_EXPIRE_DAYS = EnvUtil.get_env_var('VERIFICA_VAS_EXPIRE_DAYS', type=int, default=90)

PARERI_VERIFICA_VAS_EXPIRE_DAYS = EnvUtil.get_env_var('PARERI_VERIFICA_VAS_EXPIRE_DAYS', type=int, default=30)

CONSULTAZIONI_SCA_EXPIRE_DAYS = EnvUtil.get_env_var('CONSULTAZIONI_SCA_EXPIRE_DAYS', type=int, default=30)
PARERI_VAS_EXPIRE_DAYS = EnvUtil.get_env_var('PARERI_VAS_EXPIRE_DAYS', type=int, default=30)

ADOZIONE_RICEZIONE_PARERI_EXPIRE_DAYS = EnvUtil.get_env_var('ADOZIONE_RICEZIONE_PARERI_EXPIRE_DAYS', type=int, default=30)
ADOZIONE_RICEZIONE_OSSERVAZIONI_EXPIRE_DAYS = EnvUtil.get_env_var('ADOZIONE_RICEZIONE_OSSERVAZIONI_EXPIRE_DAYS', type=int, default=60)
ADOZIONE_VAS_PARERI_SCA_EXPIRE_DAYS = EnvUtil.get_env_var('ADOZIONE_VAS_PARERI_SCA_EXPIRE_DAYS', type=int, default=60)
ADOZIONE_VAS_PARERE_MOTIVATO_AC_EXPIRE_DAYS = EnvUtil.get_env_var('ADOZIONE_VAS_PARERE_MOTIVATO_AC_EXPIRE_DAYS', type=int, default=30)

ATTRIBUZIONE_CONFORMITA_PIT_EXPIRE_DAYS = EnvUtil.get_env_var('ATTRIBUZIONE_CONFORMITA_PIT_EXPIRE_DAYS', type=int, default=30)

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = EnvUtil.get_env_var('LANGUAGE_CODE', default='it')

LANGUAGES = (
    ("en", _("English")),
    ("it", _("Italian")),
)

USE_I18N = EnvUtil.get_env_var('USE_I18N', type=bool, default=True)
USE_L10N = EnvUtil.get_env_var('USE_L10N', type=bool, default=True)

TIME_ZONE = EnvUtil.get_env_var('TIME_ZONE', default='UTC')
USE_TZ = EnvUtil.get_env_var('USE_TZ', type=bool, default=True)

# Celery
CELERY_BROKER_URL = 'memory://'
CELERY_SCHEDULE_INTERVAL = int(os.getenv('CELERY_SCHEDULE_INTERVAL', 10))
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = TIME_ZONE
CELERY_RESULT_PERSISTENT = False
CELERY_ACKS_LATE = True
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_IGNORE_RESULT = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

CELERY_BEAT_SCHEDULE = {
    'delayed-action-sync-task': {
        'task': 'serapide_core.tasks.synch_actions',
        'schedule': timedelta(seconds=CELERY_SCHEDULE_INTERVAL),
    }
}

# CrispyForm template pack
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = EnvUtil.get_env_var(
    'DJANGO_STATIC_ROOT',
    default=str(os.path.join(os.path.dirname(BASE_DIR), 'static_root'))
)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(os.path.join(REACT_APP_DIR, 'build'), 'static')  # serapide-client
]

# Media
MEDIA_ROOT = EnvUtil.get_env_var(
    'DJANGO_STATIC_ROOT',
    default=str(os.path.join(os.path.dirname(BASE_DIR), 'media'))
)
MEDIA_URL = '/media/'

# CORS_ORIGIN_ALLOW_ALL = True
INTERNAL_IPS = EnvUtil.get_env_var('DJANGO_INTERNAL_IPS', type=list, default=[], separator=' ')

GRAPHENE = {
    'SCHEMA_INDENT': 2,
    'SCHEMA': 'serapide_core.schema.schema',
    'SCHEMA_OUTPUT': 'data/schema.json',  # defaults to schema.json
    'MIDDLEWARE': [
        'graphene_django.debug.DjangoDebugMiddleware',
        'graphene_django_extras.ExtraGraphQLDirectiveMiddleware',
    ]
}

GRAPHENE_DJANGO_EXTRAS = {
    'DEFAULT_PAGINATION_CLASS': 'graphene_django_extras.paginations.LimitOffsetGraphqlPagination',
    'DEFAULT_PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 50,
    'CACHE_ACTIVE': True,
    'CACHE_TIMEOUT': 300    # seconds
}

MIDDLEWARE = (
    # Django middleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Wagtail middleware
    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    # Django current user
    'django_currentuser.middleware.ThreadLocalUserMiddleware',
    # Strt Users middleware
    'strt_users.middleware.TokenMiddleware',
    'strt_users.middleware.SessionControlMiddleware',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d '
                      '%(thread)d %(message)s'
        },
        'simple': {
            'format': '%(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    "loggers": {
        "django": {
            "handlers": ["console"], "level": "INFO", },
        "celery": {
            "handlers": ["console"], "level": "INFO", },
        "strt_tests": {
            "handlers": ["console"], "level": "INFO", },
        "strt_portal": {
            "handlers": ["console"], "level": "INFO", },
        "strt_users": {
            "handlers": ["console"], "level": "INFO", },
        "serapide_core": {
            "handlers": ["console"], "level": "INFO", },
    },
}

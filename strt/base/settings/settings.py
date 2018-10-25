#########################################################################
#
# Copyright 2018, GeoSolutions Sas.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
#
#########################################################################


import os
from django.utils.translation import gettext_lazy as _
import dj_database_url
from .utils import EnvUtil


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.join(__file__, os.pardir))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = EnvUtil.get_env_var('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = EnvUtil.get_env_var('DJANGO_DEBUG', bool, True)

ALLOWED_HOSTS = EnvUtil.get_env_var('DJANGO_ALLOWED_HOSTS', list, [], ' ')


# Application definition

INSTALLED_APPS = [
    # StatutoTerritorioRT apps
    'base',
    'portal',
    'strt_users',
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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
]

MIDDLEWARE = [
    # Django middleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Wagtail middleware
    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = 'base.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates"),],
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

LOGOUT_REDIRECT_URL = '/'

WSGI_APPLICATION = 'base.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.parse(
        EnvUtil.get_env_var('DJANGO_DATABASE_URL',
                            default="sqlite:///{}".format(
                                os.path.join(BASE_DIR, 'db.sqlite3')))
    )
}

AUTH_USER_MODEL = 'strt_users.AppUser'

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

# WAGTAIL
WAGTAIL_SITE_NAME = 'Statuto Territorio RT'
WAGTAIL_USER_EDIT_FORM = 'strt_users.forms.AppUserEditForm'
WAGTAIL_USER_CREATION_FORM = 'strt_users.forms.AppUserCreationForm'
WAGTAIL_USER_CUSTOM_FIELDS = ['fiscal_code']
WAGTAIL_FRONTEND_LOGIN_URL = 'users/login'
WAGTAIL_FRONTEND_LOGIN_TEMPLATE = 'users/login.html'

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'it'

TIME_ZONE = 'UTC'

USE_I18N = True

LANGUAGES = (
    ("en", _("English")),
    ("it", _("Italian")),
)

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = EnvUtil.get_env_var(
    'DJANGO_STATIC_ROOT',
    default=str(os.path.join(os.path.dirname(BASE_DIR), 'static_root'))
)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Media
MEDIA_ROOT = EnvUtil.get_env_var(
    'DJANGO_STATIC_ROOT',
    default=str(os.path.join(os.path.dirname(BASE_DIR), 'media'))
)
MEDIA_URL = '/media/'
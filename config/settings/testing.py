import logging
import sys

# Graphene logs Bestiary exceptions and Django prints them
# to the standard error output. This code prevents Django
# kind of errors are not shown.
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)


# Application definition

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_TZ = True

USE_I18N = True

USE_L10N = True

# Application parameters

SECRET_KEY = 'fake-key'

INSTALLED_APPS = [
    'bestiary.core',
    'graphene_django',
    'django.contrib.auth',
    'django.contrib.contenttypes',
]

SQL_MODE = [
    'ONLY_FULL_GROUP_BY',
    'NO_ZERO_IN_DATE',
    'NO_ZERO_DATE',
    'ERROR_FOR_DIVISION_BY_ZERO',
    'NO_AUTO_CREATE_USER',
    'NO_ENGINE_SUBSTITUTION',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root',
        'PASSWORD': '',
        'NAME': 'bestiary_db',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'sql_mode': ','.join(SQL_MODE)
        },
        'TEST': {
            'NAME': 'testiary',
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_520_ci',
        }
    }
}

AUTHENTICATION_BACKENDS = [
    'graphql_jwt.backends.JSONWebTokenBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# This option should be set to True to pass
# authentication tests.
AUTHENTICATION_REQUIRED = True

GRAPHENE = {
    'SCHEMA': 'bestiary.core.schema',
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
}

import datetime
import json
import pathlib
import os

import environ

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent

env = environ.Env()
env.read_env(os.getenv('ENV_FILE', BASE_DIR.joinpath('.env')))

DEBUG = env('DJANGO_DEBUG', bool, False)

SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-dc@u$7=5l4z9$*o@trdm!0*+vif2h(csvyjg((!8ez(7e2qg+&')

ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS', list, ['localhost'])


def _debug_only(value) -> list:
    return [value] if DEBUG else []


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    *_debug_only('django.contrib.staticfiles'),
    'rest_framework',
    'app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.config.urls'

TEMPLATES = _debug_only({
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
        ],
    },
})

WSGI_APPLICATION = 'app.config.wsgi.application'

DATABASES = {'default': env.db('DJANGO_DATABASE_URL', 'psql://postgres:postgres@auth-db:5432/auth')}

AUTH_PASSWORD_VALIDATORS = []

PASSWORD_POLICY = {
    'min_length': env('PASSWORD_POLICY_MIN_LENGTH', int, 8),
    'max_length': env('PASSWORD_POLICY_MAX_LENGTH', int, 20),
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = env('DJANGO_TIME_ZONE', default='Europe/Moscow')

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR.joinpath('static')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'app.User'

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'app.api.auth.JWTAuthentication',
    ],
    'UNAUTHENTICATED_USER': None,
}

MESSAGE_BROKER = {
    'path': env('MESSAGE_BROKER_PATH', default='app.services.broker.MessageBrokerImpl'),
    'config': env('MESSAGE_BROKER_CONFIG', json.loads, {}),
}

REGISTRATION_CODE_GENERATOR = {
    'path': env(
        'REGISTRATION_CODE_GENERATOR_PATH',
        default='app.services.registration_code.RegistrationCodeGeneratorImpl',
    ),
    'config': env('REGISTRATION_CODE_GENERATOR_CONFIG', json.loads, {'code_length': 20}),
}

_JWT_TOKEN_SERVICE_CONFIG_INSECURE_DEFAULTS = {
    'access_secret': 'insecure-jwt-access-secret',
    'access_expires_minutes': 15,
    'refresh_secret': 'insecure-jwt-refresh-secret',
    'refresh_expires_minutes': 14 * 24 * 60,
    'algorithm': 'HS256',
}

JWT_TOKEN_SERVICE_CONFIG = {
    'path': env('JWT_TOKEN_SERVICE_PATH', default='app.services.jwt_token.JwtTokenServiceImpl'),
    'config': env('JWT_TOKEN_SERVICE_CONFIG', json.loads, _JWT_TOKEN_SERVICE_CONFIG_INSECURE_DEFAULTS),
}

from pathlib import Path
from datetime import timedelta
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8u923hr45677ujhbvcde4r56789pedasc9ijnjk192e8uwydgvdbhnjkiudwyhdn2j1ie837eyftrsdghsj'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['1509.ddns.net', 'localhost']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'django_extensions',

    # Local Apps
    'helpers',
    'userprofile',
    'organization',
    'problem',
    'judger',
    'submission',
    'compete', # 'contest' is a Python module already
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bkdnoj.urls'

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

WSGI_APPLICATION = 'bkdnoj.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'

# Fixture folder
FIXTURE_DIRS = [ os.path.join(BASE_DIR, 'bkdnoj', 'fixture'), ]

# Media files (uploaded)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL=True
# CORS_ALLOWED_ORIGINS = [
#     'http://localhost:3000', 'http://1509.dns.net:3000',
# ]

CSRF_COOKIE_HTTPONLY = False
CSRF_TRUSTED_ORIGINS = ['http://1509.ddns.net:3000', 'http://localhost:3000']

# REST Framework settings
REST_FRAMEWORK = {
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_PAGINATION_CLASS': 'helpers.custom_pagination.PageCountPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

# SimpleJWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=180),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        # 'django.db.backends': {
        #     'handlers': ['console'],
        #     'level': 'DEBUG',
        # },
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# --------- Site settings
BKDNOJ_PROBLEM_DATA_ROOT=os.path.join(MEDIA_ROOT, 'problem_data')
BKDNOJ_PROBLEM_PDF_ROOT=os.path.join(MEDIA_ROOT, 'problem_pdf')
BKDNOJ_PROBLEM_MIN_PROBLEM_POINTS = 0.0
BKDNOJ_PROBLEM_MAX_TIME_LIMIT=20.0 # 20 seconds
BKDNOJ_PROBLEM_MIN_TIME_LIMIT=0.1 # 0.1 second = 100 milliseconds
BKDNOJ_PROBLEM_MAX_MEMORY_LIMIT=1024*1024 # 1024*1024 kB = 1024 MB = 1GB
BKDNOJ_PROBLEM_MIN_MEMORY_LIMIT=64*1024 # 64*1024 KB = 64 MB
BKDNOJ_PROBLEM_ACCEPTABLE_STATEMENT_PDF = set(['statement.pdf', 'problem.pdf', 'prob.pdf'])
BKDNOJ_PROBLEM_STATEMENT_PDF_FILENAME   = 'problem.pdf'
BKDNOJ_PROBLEM_DATA_IN_FILE_EXT         = ('.in',  '.input',  '.inp', '.i', )
BKDNOJ_PROBLEM_DATA_ANS_FILE_EXT        = ('.out', '.output', '.ans', '.a', )
BKDNOJ_PROBLEM_ACCEPTABLE_CONFIG_EXT = set(['.ini', '.conf'])
BKDNOJ_PROBLEM_CONFIG_TOKEN_LENGTH = 2**16
BKDNOJ_SUBMISSION_LIMIT = 3
BKDNOJ_SUBMISSION_OUTPUT_PREFIX = 200
BKDNOJ_SUBMISSION_OUTPUT_LIMIT = int(1e12)

#
EVENT_DAEMON_USE = False
EVENT_DAEMON_POST = 'ws://localhost:9997/'
EVENT_DAEMON_GET = 'ws://localhost:9996/'
EVENT_DAEMON_POLL = '/channels/'
EVENT_DAEMON_KEY = None
EVENT_DAEMON_AMQP_EXCHANGE = 'bkdnoj-events'
EVENT_DAEMON_SUBMISSION_KEY = '6Sdmkx^%pk@GsifDfXcwX*Y7LRF%RGT8vmFpSxFBT$fwS7trc8raWfN#CSfQuKApx&$B#Gh2L7p%W!Ww'

# -- Judger Bridge
BRIDGED_JUDGE_ADDRESS = [('localhost', 9999)]
BRIDGED_JUDGE_PROXIES = None
BRIDGED_DJANGO_ADDRESS = [('localhost', 9998)]
BRIDGED_DJANGO_CONNECT = None

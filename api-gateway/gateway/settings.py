import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'api-gateway-secret-key-change-in-production'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'rest_framework',
    'corsheaders',
    'gateway',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'gateway.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://frontend:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'origin',
    'x-customer-id',
    'x-staff-token',
    'x-requested-with',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
}

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

APPEND_SLASH = False

# Internal service URLs
CUSTOMER_SERVICE = os.environ.get('CUSTOMER_SERVICE_URL', 'http://customer-service:8000')
STAFF_SERVICE = os.environ.get('STAFF_SERVICE_URL', 'http://staff-service:8000')
MOBILE_SERVICE = os.environ.get('MOBILE_SERVICE_URL', 'http://mobile-service:8000')
DESKTOP_SERVICE = os.environ.get('DESKTOP_SERVICE_URL', 'http://desktop-service:8000')
CART_SERVICE = os.environ.get('CART_SERVICE_URL', 'http://cart-service:8000')
CLOTHES_SERVICE = os.environ.get('CLOTHES_SERVICE_URL', 'http://clothes-service:8000')
AI_SERVICE = os.environ.get('AI_SERVICE_URL', 'http://ai-service:8000')

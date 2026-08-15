"""
Django settings for config project.

Configured for local development and cloud production (Render + Neon).
"""

import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================
# 1. SECURITY & ENVIRONMENT CONFIGURATION
# ==========================================

# Pulls SECRET_KEY from environment variables on Render, falls back to dev key locally
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-rdiu*vmf0)9zurdh(nijpv0tm76y-sv2dhg9ve!k1h7kgqgre('
)

# DEBUG is True locally, but False if explicitly set to 'False' in cloud environment
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Allow Render domains, local interfaces, and any wildcard host on cloud
ALLOWED_HOSTS = ['*']


# ==========================================
# 2. APPLICATION DEFINITIONS
# ==========================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-Party Libraries
    'rest_framework',
    'corsheaders',

    # Enguli Project Modular Apps
    'stations',
    'telemetry',
    'analytics',
    'alerts',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be at the very top for DRF CORS handling
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise for high-speed cloud static assets
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ==========================================
# 3. DATABASE CONFIGURATION (DUAL-MODE)
# ==========================================
# If DATABASE_URL is set (Render/Neon), parse it with SSL.
# Otherwise, fall back to your local PostgreSQL setup automatically.

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'enguli_db',
            'USER': 'postgres',
            'PASSWORD': 'Keystone',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }


# ==========================================
# 4. PASSWORD VALIDATION & LOCALIZATION
# ==========================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ==========================================
# 5. STATIC FILES & WHITENOISE STORAGE
# ==========================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Compressed storage with caching for optimal performance on cloud web services
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ==========================================
# 6. CORS & ORIGIN WHITELISTING
# ==========================================

# When deploying to production, allow your local ports + any live Vercel frontend domains
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
]

# Allows public requests from your ESP32 microcontroller or deployed Vercel frontend
CORS_ALLOW_ALL_ORIGINS = True
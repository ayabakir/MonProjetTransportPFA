from pathlib import Path
import os
from dotenv import load_dotenv
from environ import Env
env = Env()
env.read_env()

BASE_URL = "http://localhost:8000"


ORS_API_KEY = os.getenv('ORS_API_KEY')
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, '.env')) #jh
# Ou si vous utilisez python-dotenv
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
print(f"--- DEBUG SETTINGS: La clé secrète lue est : '{STRIPE_SECRET_KEY}' ---") # <--- AJOUTEZ CETTE LIGNE
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-s@js#x@dvy%*lt!fg#vo@64_=5x3b&&itffcj2aab_u%!b+fws'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [ayaba.pythonanywhere.com]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'transport',
    'widget_tweaks',
    'a_stripe',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', # <--- ICI
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', # <--- APRES SessionMiddleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'systeme_transport_config.urls'

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

WSGI_APPLICATION = 'systeme_transport_config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Dans settings.py
ADRESSE_DEPOT_PRINCIPAL = "Km 8 Route d'El Jadida, Lissasfa, Casablanca, Maroc" # METTEZ UNE VRAIE ADRESSE TESTABLE
# Le prix de base pour toute commande, indépendamment du poids ou de la distance.
PRIX_BASE = 25.00  # Exemple : 25 MAD

# Le prix additionnel par kilogramme.
PRIX_PAR_KG = 2.50  # Exemple : 2.50 MAD par kg

# Le prix additionnel par kilomètre.
PRIX_PAR_KM = 3.00  # Exemple : 3.00 MAD par km

STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY_TEST', default="secret")
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default="webhook")


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# systeme_transport_config/settings.py

from pathlib import Path
import os
from environ import Env  # Nous gardons uniquement django-environ

# Initialisation de django-environ au début du fichier
env = Env()
Env.read_env(os.path.join(Path(__file__).resolve().parent.parent, '.env'))

# --- CONFIGURATION DE BASE ---
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_URL = "http://localhost:8000" # Cette variable sera peut-être à revoir si vous l'utilisez pour des URLs absolues

# --- CLÉS SECRÈTES ET VARIABLES D'ENVIRONNEMENT ---
# MODIFIÉ POUR PRODUCTION : La clé secrète est maintenant chargée depuis les variables d'environnement
SECRET_KEY = env('DJANGO_SECRET_KEY')

ORS_API_KEY = env('ORS_API_KEY', default='votre_valeur_par_defaut_si_besoin')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY_TEST') # On garde la version propre avec env()
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET')

# --- CONFIGURATION DE DÉPLOIEMENT ---
# MODIFIÉ POUR PRODUCTION : DEBUG est False pour la sécurité
DEBUG = False

# MODIFIÉ POUR PRODUCTION : Remplacez 'ayaba' par votre nom d'utilisateur PythonAnywhere
ALLOWED_HOSTS = ['ayaba.pythonanywhere.com', '127.0.0.1', 'localhost']

# --- APPLICATIONS ET MIDDLEWARE ---
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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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

# --- BASE DE DONNÉES ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- VALIDATION DE MOTS DE PASSE ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- INTERNATIONALISATION ---
LANGUAGE_CODE = 'fr-fr' # Changé pour le français, à adapter si besoin
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# --- FICHIERS STATIQUES ET MÉDIAS ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
# AJOUTÉ POUR PRODUCTION : Indispensable pour la commande collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # Typo corrigée

# --- CONFIGURATIONS MÉTIER ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
ADRESSE_DEPOT_PRINCIPAL = "Km 8 Route d'El Jadida, Lissasfa, Casablanca, Maroc"
PRIX_BASE = 25.00
PRIX_PAR_KG = 2.50
PRIX_PAR_KM = 3.00
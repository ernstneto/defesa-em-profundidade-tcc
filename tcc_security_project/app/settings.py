# app/settings.py

from pathlib import Path
import os
import socket # Importar socket no topo
from dotenv import load_dotenv

# Carrega as variaveis do arquivo .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-key')

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

DEBUG = os.getenv('DEBUG', 'False') == 'True'
"""
# --- LISTAS ESTÁTICAS INICIAIS ---
ALLOWED_HOSTS = [
    '*',
    'localhost',
    '127.0.0.1',
    # IPs Estáticos do seu ambiente (para falha de detecção)
    '192.168.1.200', # PfSense WAN
    '172.16.10.1',  # PfSense LAN
    '172.16.10.2',  # VM Servidora LAN
    '172.16.10.101', # VM Servidora LAN DHCP
]
"""
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS','*').split(',')
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'rangefilter',
    'comments',
    'accounts',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'documents',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'comments.middleware.RateLimitMiddleware',
    'accounts.middleware.SessionIPProtectionMiddleware',
    
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'app.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': '5432',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# --- LISTA DE ORIGENS CSRF ESTÁTICAS INICIAIS ---
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'https://localhost:8443',
    #'https://preroyal-alexzander-unexcogitable.ngrok-free.dev',
    'https://192.168.1.200:8443',
    'http://192.168.1.200:8000',
    'https://172.16.10.2:8443',
    'http://172.16.10.2:8000',
    'http://172.16.10.101:8000',
    'https://172.16.10.101:8443',
    'https://*.trycloudflare.com', # Curinga para Cloudflare
    'https://*.ngrok-free.app',
]

# Sessão/Login/Site
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'welcome'
SESSION_COOKIE_AGE = 600
SESSION_SAVE_EVERY_REQUEST = True
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SITE_ID = 1
SECURE_CHECK_SSL = False

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Proxy Headers
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailOrUsernameBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Logging Configuration
LOGS_DIR = BASE_DIR / 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'colored_console': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(levelname)-8s %(asctime)s %(name)-12s %(message)s',
            'log_colors': {
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
            },
        },
        'file': {
            'format': '%(levelname)-8s %(asctime)s %(name)-12s %(module)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored_console',
        },
        'general_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'general.log',
            'formatter': 'file',
        },
        'blacklist_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'blacklist.log',
            'formatter': 'file',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'general_file'],
            'level': 'INFO',
        },
        'blacklist_events': {
            'handlers': ['console', 'blacklist_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django': {
            'handlers': ['console', 'general_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# --- CÓDIGO DE DETECÇÃO DINÂMICA DE IP (MOVEU PARA O FINAL) ---
try:
    # Descobre o nome do host e o IP local da máquina
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"**** IP: {local_ip} ****")
    # Tenta descobrir IPs adicionais (caso tenha múltiplas interfaces)
    additional_ips = []
    try:
        # Conecta num IP externo fictício para saber qual interface é a rota padrão
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        detected_ip = s.getsockname()[0]
        additional_ips.append(detected_ip)
        s.close()
    except:
        pass

except Exception as e:
    print(f"Erro ao detectar IP automaticamente: {e}")
    local_ip = '127.0.0.1'
    additional_ips = []

# Adiciona o IP local detectado (se já não estiver lá)
if local_ip not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(local_ip)
    CSRF_TRUSTED_ORIGINS.append(f'http://{local_ip}:8000')
    CSRF_TRUSTED_ORIGINS.append(f'https://{local_ip}:8443')

# Adiciona IPs adicionais detectados
for ip in additional_ips:
    if ip not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(ip)
        CSRF_TRUSTED_ORIGINS.append(f'http://{ip}:8000')
        CSRF_TRUSTED_ORIGINS.append(f'https://{ip}:8443')

for ips in CSRF_TRUSTED_ORIGINS:
    print(f"ip: {ips}")

# ----- MOBILE -----

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

CORS_ALLOW_ORIGINS = True # Permite que o app acesse de qualquer lugar

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
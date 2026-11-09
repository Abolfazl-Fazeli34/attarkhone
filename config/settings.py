import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv(BASE_DIR / '.env')

# افزودن پوشه apps به مسیرهای پایتون
sys.path.insert(0, str(BASE_DIR / 'apps'))

# کلید امنیتی جنگو
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-attarkhone-secret-key-podman2-shabake-212290')

# وضعیت حالت دیباگ (پیش‌فرض True، در داکر پروداکشن False)
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [h.strip() for h in os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',') if h.strip()]

# پشتیبانی از پروکسی معکوس وب‌سرور (Nginx) جهت تشخیص پروتکل SSL و هاست دامنه
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# پایگاه دامنه‌های مجاز برای اعتبارسنجی CSRF
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]
default_origins = [
    'http://127.0.0.1:8650', 'http://localhost:8650',
    'http://127.0.0.1:8001', 'http://localhost:8001',
    'http://127.0.0.1:8000', 'http://localhost:8000',
    'http://*.ip3.ir', 'https://*.ip3.ir',
    'http://attarkhone.ip3.ir', 'https://attarkhone.ip3.ir',
    'http://*.ir', 'https://*.ir',
    'http://*.com', 'https://*.com',
    'http://*.org', 'https://*.org',
    'http://*.net', 'https://*.net',
]
for origin in default_origins:
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    # اپلیکیشن‌های اختصاصی عطارخونه (پودمان ۲)
    'accounts',
    'core',
    'catalog',
    'shipping',
    'orders',
    'marketing',
    'pages',
    'remedy',
]

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # پشتیبانی پویا از دامنه‌ها در برابر خطای CSRF
    'core.middleware.DynamicCsrfTrustedOriginsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # کارگاه ۳: میدلور حالت تعمیرات و وایت‌لیست IP
    'core.middleware.MaintenanceModeMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                # پردازنده سراسری اطلاعات فروشگاه، سبد خرید و منو
                'core.context_processors.store_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DB_DIR = os.getenv('DJANGO_DB_DIR')
if DB_DIR:
    os.makedirs(DB_DIR, exist_ok=True)
    DB_PATH = Path(DB_DIR) / 'db.sqlite3'
else:
    DB_PATH = BASE_DIR / 'db.sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
]

# تنظیمات زبان، تقویم و منطقه زمانی (کارگاه ۱۹)
LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

# مسیرهای فایل‌های ایستا (CSS, JS, Fonts)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# فایل‌های رسانه (تصاویر محصولات، اسلایدرها و فیش‌های بانکی)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# پشتیبانی از احراز هویت با نام کاربری یا نشانی ایمیل
AUTHENTICATION_BACKENDS = [
    'accounts.backends.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# تنظیمات ارسال ایمیل واقعی (Gmail SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'abolfazlfazeli760@gmail.com'
EMAIL_HOST_PASSWORD = 'wybilntwgfhosibv'
DEFAULT_FROM_EMAIL = 'عطارخونه <abolfazlfazeli760@gmail.com>'
SERVER_EMAIL = 'abolfazlfazeli760@gmail.com'

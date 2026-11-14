#!/bin/sh
set -e

echo "=========================================================="
echo "    سامانه فروشگاه آنلاین گیاهان دارویی عطارخونه          "
echo "    راه‌اندازی سرویس در محیط پروداکشن کانتینر داکر         "
echo "=========================================================="

# اعمال مایگریشن‌های پایگاه داده
echo "[1/3] در حال اجرای مایگریشن‌های پایگاه داده..."
python manage.py migrate --noinput

# گردآوری و فشرده‌سازی فایل‌های استاتیک توسط WhiteNoise
echo "[2/3] در حال گردآوری فایل‌های استاتیک (CollectStatic)..."
python manage.py collectstatic --noinput

# حصول اطمینان از وجود پوشه‌ها و دارایی‌های رسانه‌ای اولیه (لوگو و آیکون برند)
mkdir -p /app/media/settings
if [ ! -f /app/media/settings/logo.png ] && [ -f /app/static/img/brand_logo.png ]; then
    echo "بارگذاری لوگو و آیکون پیش‌فرض برند در رسانه..."
    cp /app/static/img/brand_logo.png /app/media/settings/logo.png
    cp /app/static/img/brand_icon.png /app/media/settings/favicon.png
fi

# بررسی نیاز به استقرار دیتای پروداکشن اولیه در صورت خالی بودن دیتابیس
echo "[3/3] بررسی داده‌های اولیه پایگاه داده..."
python manage.py shell -c "
from catalog.models import Product
if Product.objects.count() == 0:
    print('پایگاه داده خالی است. در حال استقرار دیتای اولیه پروداکشن...')
    from django.core.management import call_command
    call_command('seed_production_data')
else:
    print(f'داده‌ها از قبل موجود است: {Product.objects.count()} محصول فعال.')
"

# اجرای سرور پروداکشن Gunicorn
PORT_NUM=${PORT:-8650}
WORKERS_NUM=${GUNICORN_WORKERS:-3}
echo "اجرای سرور پروداکشن Gunicorn بر روی درگاه 0.0.0.0:$PORT_NUM با $WORKERS_NUM کارگر پردازشی..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:$PORT_NUM \
    --workers $WORKERS_NUM \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

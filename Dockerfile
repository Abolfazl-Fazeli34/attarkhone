# تصویر پایه رسمی پایتون ۳.۱۲ نسخه سبک و بهینه اسلیم
FROM python:3.12-slim

# تنظیم متغیرهای محیطی پایتون
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8001

# دایرکتوری کاری پروژه در کانتینر
WORKDIR /app

# کپی بسته‌های لوکال چرخ‌ها (Wheels) و نصب کاملاً آفلاین و سریع
COPY wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*.whl && \
    rm -rf /wheels

# کپی کدهای پروژه به کانتینر
COPY . /app/

# ایجاد دایرکتوری‌های رسانه و پایگاه داده و تنظیم مجوز اجرا
RUN mkdir -p /app/staticfiles /app/media /app/data && \
    chmod +x /app/entrypoint.sh

# درگاه اختصاصی پروژه
EXPOSE 8001

# پایش سلامت خودکار کانتینر با پایتون داخلی
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8001/health/')" || exit 1

# اسکریپت ورود به کانتینر
ENTRYPOINT ["/app/entrypoint.sh"]

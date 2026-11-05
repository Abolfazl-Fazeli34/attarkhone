import os
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core import management
from django.conf import settings


class Command(BaseCommand):
    help = "کارگاه ۲۰ کتاب: تهیه نسخه پشتیبان از پایگاه داده و فایل‌های رسانه فروشگاه"

    def handle(self, *args, **options):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        backup_file = os.path.join(backup_dir, f"backup_attarkhone_{timestamp}.json")
        self.stdout.write(f"در حال ایجاد فایل پشتیبان پایگاه داده: {backup_file} ...")

        with open(backup_file, 'w', encoding='utf-8') as f:
            management.call_command('dumpdata', indent=2, stdout=f, exclude=['contenttypes', 'auth.Permission'])

        # کپی فایل دیتابیس sqlite3 در صورت وجود
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            db_backup_path = os.path.join(backup_dir, f"db_sqlite3_{timestamp}.bak")
            shutil.copy2(db_path, db_backup_path)

        self.stdout.write(self.style.SUCCESS(f"✓ نسخه پشتیبان کامل با موفقیت در پوشه backups ایجاد شد:\n  {backup_file}"))

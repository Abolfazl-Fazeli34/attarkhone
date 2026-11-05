import os
from django.core.management.base import BaseCommand
from django.core import management
from django.conf import settings


class Command(BaseCommand):
    help = "کارگاه ۲۰ کتاب: بازیابی اطلاعات فروشگاه از فایل نسخه پشتیبان"

    def add_arguments(self, parser):
        parser.add_argument(
            'backup_file',
            nargs='?',
            type=str,
            help='مسیر فایل پشتیبان JSON جهت بازیابی (اختیاری؛ در صورت خالی بودن آخرین بکاپ انتخاب می‌شود)',
        )

    def handle(self, *args, **options):
        backup_file = options.get('backup_file')
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')

        if not backup_file:
            if not os.path.exists(backup_dir):
                self.stdout.write(self.style.ERROR("پوشه پشتیبان‌ها یافت نشد."))
                return
            json_files = sorted([f for f in os.listdir(backup_dir) if f.endswith('.json')])
            if not json_files:
                self.stdout.write(self.style.ERROR("هیچ فایل بکاپی یافت نشد."))
                return
            backup_file = os.path.join(backup_dir, json_files[-1])

        self.stdout.write(f"در حال بازیابی اطلاعات از فایل: {backup_file} ...")
        management.call_command('loaddata', backup_file)
        self.stdout.write(self.style.SUCCESS("✓ بازیابی نسخه پشتیبان با موفقیت به پایان رسید (کارگاه ۲۰)."))

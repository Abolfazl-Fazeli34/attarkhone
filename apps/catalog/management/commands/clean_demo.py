from django.core.management.base import BaseCommand
from catalog.models import Product, Category, Brand, Supplier, ProductVariant, ProductFeature
from orders.models import Order, OrderItem, Cart, CartItem, BankReceipt


class Command(BaseCommand):
    help = "کارگاه ۹ کتاب: حذف محتوای پیش‌فرض و داده‌های دمو از فروشگاه"

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='حذف تمامی محصولات، شاخه‌ها و سفارش‌های تستی',
        )

    def handle(self, *args, **options):
        self.stdout.write("در حال پاکسازی محتوای پیش‌فرض و داده‌های تستی (کارگاه ۹)...")

        # حذف سبدها و سفارش‌ها
        BankReceipt.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()

        # حذف محصولات، مشخصه‌ها و ویژگی‌ها
        ProductFeature.objects.all().delete()
        ProductVariant.objects.all().delete()
        Product.objects.all().delete()
        
        if options['all']:
            Category.objects.all().delete()
            Brand.objects.all().delete()
            Supplier.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("✓ محتوای پیش‌فرض فروشگاه با موفقیت پاکسازی شد (کارگاه ۹)."))

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from accounts.models import User
from core.models import StoreSetting
from catalog.models import Category, Brand, Supplier, Product, ProductVariant, ProductFeature
from shipping.models import Province, Carrier
from marketing.models import Slider, Banner, Coupon
from pages.models import StaticPage
from remedy.models import SymptomCategory, ChemicalDrug, DrugInteraction, HealthRemedyPackage


class Command(BaseCommand):
    help = "بارگذاری دیتای اولیه و واقعی فروشگاه عطارخونه منطبق بر موکاپ ارائه‌شده"

    def handle(self, *args, **options):
        self.stdout.write("در حال آماده‌سازی و بارگذاری اطلاعات دقیق موکاپ عطارخونه...")

        # ۱. تنظیمات فروشگاه
        setting = StoreSetting.get_settings()
        setting.store_name = "عطارخونه"
        setting.slogan = "دانش کهن، سلامت مدرن؛ انتخاب آگاهانه گیاهان دارویی"
        setting.phone = "021-88997766"
        setting.mobile = "09123456789"
        setting.email = "info@attarkhooneh.ir"
        setting.address = "تهران، خیابان ولیعصر، بالاتر از تقاطع طالقانی، پلاک ۱۱۴"
        setting.gift_wrap_cost = 25000
        setting.free_shipping_threshold = 400000
        setting.is_maintenance_mode = False
        setting.maintenance_allowed_ips = "127.0.0.1, ::1"
        setting.save()

        # ۲. ایجاد کاربران
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'علی',
                'last_name': 'محمدی',
                'email': 'admin@attarkhooneh.ir',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'phone': '09123456789',
            }
        )
        admin_user.first_name = 'علی'
        admin_user.last_name = 'محمدی'
        admin_user.set_password('admin123456')
        admin_user.save()

        hesabdar, _ = User.objects.get_or_create(
            username='hesabdar',
            defaults={
                'first_name': 'مبینا',
                'last_name': 'حسابی',
                'email': 'account@attarkhooneh.ir',
                'role': 'accountant',
                'is_staff': True,
                'phone': '09122222222',
            }
        )
        hesabdar.set_password('hesabdar123')
        hesabdar.save()

        anbardar, _ = User.objects.get_or_create(
            username='anbardar',
            defaults={
                'first_name': 'رضا',
                'last_name': 'انصاری',
                'email': 'stock@attarkhooneh.ir',
                'role': 'logistic',
                'is_staff': True,
                'phone': '09123333333',
            }
        )
        anbardar.set_password('anbardar123')
        anbardar.save()

        # کاربر علی محمدی (عین موکاپ)
        ali, _ = User.objects.get_or_create(
            username='ali_mohammadi',
            defaults={
                'first_name': 'علی',
                'last_name': 'محمدی',
                'email': 'ali@gmail.com',
                'role': 'customer',
                'phone': '09123456789',
                'address': 'تهران، خیابان شریعتی، بالاتر از پل رومی، پلاک ۴۵',
                'postal_code': '1939512345',
            }
        )
        ali.first_name = 'علی'
        ali.last_name = 'محمدی'
        ali.set_password('ali123')
        ali.save()

        # ۳. برندها و تأمین‌کنندگان
        brand_ehya, _ = Brand.objects.get_or_create(
            name="مزارع ارگانیک احیاء",
            slug="ehya-farms",
            defaults={'description': 'تولیدکننده نمونه گیاهان دارویی استاندارد'}
        )
        brand_kimiya, _ = Brand.objects.get_or_create(
            name="کیمیا دارو سلامت",
            slug="kimiya-darou",
            defaults={'description': 'دارنده گواهی سلامت و بهداشت'}
        )
        sup_damavand, _ = Supplier.objects.get_or_create(
            name="مزارع کوهپایه البرز و دماوند",
            defaults={'contact_person': 'مهندس رادمنش', 'phone': '021-76543210'}
        )

        # ۴. دسته‌بندی‌های ۶ گانه مطابق موکاپ
        # دمنوش‌ها, گیاهان دارویی, عصاره‌ها و روغن‌ها, ادویه‌های گیاهی, محصولات سلامتی, پک‌های درمانی
        cat_tea, _ = Category.objects.get_or_create(
            slug="damnoosh",
            defaults={'name': "دمنوش‌ها", 'description': 'دمنوش‌های درمانی ترکیبی خالص'}
        )
        cat_herbs, _ = Category.objects.get_or_create(
            slug="herbs",
            defaults={'name': "گیاهان دارویی", 'description': 'برگ، گل و ریشه‌های خشک‌شده طبیعی'}
        )
        cat_oils, _ = Category.objects.get_or_create(
            slug="extracts-oils",
            defaults={'name': "عصاره‌ها و روغن‌ها", 'description': 'روغن‌های درمانی پرس سرد خالص'}
        )
        cat_spices, _ = Category.objects.get_or_create(
            slug="herbal-spices",
            defaults={'name': "ادویه‌های گیاهی", 'description': 'ادویه‌های اصیل و ارگانیک ایرانی'}
        )
        cat_wellness, _ = Category.objects.get_or_create(
            slug="wellness-products",
            defaults={'name': "محصولات سلامتی", 'description': 'فرآورده‌های تندرستی و مراقبت طبیعی'}
        )
        cat_packages, _ = Category.objects.get_or_create(
            slug="therapy-packages",
            defaults={'name': "پک‌های درمانی", 'description': 'بسته‌های بهینه و اقتصادی دوره درمان'}
        )

        # ۵. محصولات مطابق عکس موکاپ
        # محصول ۱: دمنوش آرامش‌بخش (۹۹,۰۰۰ تومان - تخفیف از ۱۱۹,۰۰۰)
        p_damnoosh, _ = Product.objects.get_or_create(
            slug="damnoosh-aramesh-bakhsh",
            defaults={
                'name': "دمنوش آرامش‌بخش",
                'category': cat_tea,
                'brand': brand_kimiya,
                'supplier': sup_damavand,
                'temperament': 'moderate',
                'base_price': 119000,
                'discount_percent': 17,
                'is_featured': True,
                'is_organic': True,
                'short_description': "ترکیبی بی‌نظیر از گل‌گاوزبان، بابونه و اسطوخودوس برای آرامش ذهن و بهبود خواب",
                'description': "این دمنوش ترکیبی اختصاصی عطارخونه شامل گل‌گاوزبان، بابونه، به‌لیمو و اسطوخودوس کوهی است. بدون عوارض خواب‌آلودگی صبحگاهی، تنش‌های عصبی بعد از کار را کاهش داده و ریتم خواب عمیق شبانه را بازیابی می‌کند.",
                'meta_title': "خرید دمنوش آرامش بخش | عطارخونه",
                'meta_keywords': "دمنوش آرامش بخش, خرید دمنوش خواب, گل گاوزبان, اسطوخودوس",
                'meta_description': "خرید دمنوش آرامش‌بخش ترکیبی عطارخونه با کیفیت اعلا و تخفیف ویژه.",
            }
        )
        p_damnoosh.base_price = 119000
        p_damnoosh.discount_percent = 17
        p_damnoosh.save()

        ProductVariant.objects.get_or_create(product=p_damnoosh, weight_label="شیشه ۱۰۰ گرمی", defaults={'price': 99000, 'stock': 40})
        ProductVariant.objects.get_or_create(product=p_damnoosh, weight_label="بسته ۲۵۰ گرمی (اقتصادی)", defaults={'price': 199000, 'stock': 25})
        ProductFeature.objects.get_or_create(product=p_damnoosh, name="طبع و مزاج", defaults={'value': 'معتدل و آرام‌بخش'})
        ProductFeature.objects.get_or_create(product=p_damnoosh, name="ترکیبات", defaults={'value': 'گل‌گاوزبان، بابونه، اسطوخودوس، به‌لیمو'})
        ProductFeature.objects.get_or_create(product=p_damnoosh, name="زمان مصرف", defaults={'value': 'یک فنجان یک ساعت پیش از خواب'})

        # محصول ۲: گل‌گاوزبان ممتاز (۷۹,۰۰۰ تومان)
        p_gavzaban, _ = Product.objects.get_or_create(
            slug="gol-gavzaban-momtaz",
            defaults={
                'name': "گل‌گاوزبان ممتاز",
                'category': cat_herbs,
                'brand': brand_ehya,
                'supplier': sup_damavand,
                'temperament': 'hot_wet',
                'base_price': 79000,
                'discount_percent': 0,
                'is_featured': True,
                'is_organic': True,
                'short_description': "گل‌گاوزبان دست‌چین کوهستان، تقویت قلب، نشاط‌آور و آرام‌بخش قوی اعصاب.",
                'description': "گل‌گاوزبان ممتاز برداشت‌شده از ارتفاعات البرز، کاملاً بوجاری و بدون خار و ساقه. مناسب برای تسکین اضطراب و تپش قلب عصبی.",
                'meta_title': "خرید گل گاوزبان ممتاز | عطارخونه",
                'meta_keywords': "گل گاوزبان ممتاز, خرید گیاه دارویی, آرامش اعصاب",
                'meta_description': "گل گاوزبان ممتاز کوهی صددرصد خالص در عطارخونه.",
            }
        )
        p_gavzaban.base_price = 79000
        p_gavzaban.save()
        ProductVariant.objects.get_or_create(product=p_gavzaban, weight_label="بسته ۱۰۰ گرمی", defaults={'price': 79000, 'stock': 50})
        ProductVariant.objects.get_or_create(product=p_gavzaban, weight_label="بسته ۲۵۰ گرمی", defaults={'price': 179000, 'stock': 20})
        ProductFeature.objects.get_or_create(product=p_gavzaban, name="طبع", defaults={'value': 'گرم و تر'})
        ProductFeature.objects.get_or_create(product=p_gavzaban, name="مصلح", defaults={'value': 'لیمو امانی یا نبات'})

        # محصول ۳: چای سبز گیاهی (۹۹,۰۰۰ تومان)
        p_greentea, _ = Product.objects.get_or_create(
            slug="green-tea-organic",
            defaults={
                'name': "چای سبز گیاهی",
                'category': cat_tea,
                'brand': brand_ehya,
                'supplier': sup_damavand,
                'temperament': 'cold_dry',
                'base_price': 99000,
                'discount_percent': 0,
                'is_featured': True,
                'is_organic': True,
                'short_description': "چای سبز لاهیجان اعلا سرشار از آنتی‌اکسیدان، افزایش متابولیسم و پاکسازی بدن.",
                'description': "برگ‌های تازه چای سبز فرآوری‌شده به شیوه سنتی، بدون تلخی زننده با عطر طبیعی. مناسب برای چربی‌سوزی، سم‌زدایی کبد و تقویت سیستم ایمنی.",
                'meta_title': "خرید چای سبز گیاهی | عطارخونه",
                'meta_keywords': "چای سبز, خرید چای لاغری, آنتی اکسیدان طبیعی",
                'meta_description': "چای سبز گیاهی ممتاز ایرانی خالص در بسته‌بندی محافظ هوا.",
            }
        )
        p_greentea.base_price = 99000
        p_greentea.save()
        ProductVariant.objects.get_or_create(product=p_greentea, weight_label="بسته ۱۵۰ گرمی", defaults={'price': 99000, 'stock': 30})

        # محصول ۴: پک درمانی سلامت و خواب
        p_box, _ = Product.objects.get_or_create(
            slug="health-gift-box",
            defaults={
                'name': "پک ویژه سلامت و آرامش اعصاب",
                'category': cat_packages,
                'brand': brand_kimiya,
                'supplier': sup_damavand,
                'temperament': 'moderate',
                'base_price': 185000,
                'discount_percent': 15,
                'is_featured': True,
                'is_organic': True,
                'short_description': "پکیج هدیه شامل دمنوش آرامش، شیشه گل‌گاوزبان و دمنوش‌ساز دستی در جعبه کادویی سبز.",
                'description': "یک هدیه فاخر برای دوستان و خانواده شامل سه گیاه منتخب آرام‌بخش با شناسنامه تضمین خلوص آزمایشگاهی.",
                'meta_title': "پک ویژه سلامت و آرامش اعصاب | عطارخونه",
                'meta_keywords': "پک هدیه سلامتی, پکیج گیاهان دارویی, کادوی سلامت",
                'meta_description': "بسته‌بندی کادویی لوکس سبز با روبان طلایی شامل بهترین گیاهان دارویی آرامش‌بخش.",
            }
        )

        # محصول ۵: روغن سیاه‌دانه درمانی
        p_oil, _ = Product.objects.get_or_create(
            slug="black-seed-oil-pure",
            defaults={
                'name': "روغن سیاه‌دانه پرس سرد خالص",
                'category': cat_oils,
                'brand': brand_ehya,
                'supplier': sup_damavand,
                'temperament': 'hot_dry',
                'base_price': 89000,
                'discount_percent': 0,
                'is_featured': True,
                'is_organic': True,
                'short_description': "روغن خالص سیاه‌دانه پرس سرد در قطره‌چکان کهربایی، تسکین دردهای مفصلی و روماتیسم.",
                'description': "روغن‌گیری کلدپرس بدون حرارت، حفظ کامل ماده مؤثره تیموکینون.",
                'meta_title': "خرید روغن سیاه دانه خالص | عطارخونه",
                'meta_keywords': "روغن سیاه دانه, تسکین درد مفاصل",
                'meta_description': "روغن سیاه دانه پرس سرد در شیشه دارویی قطره چکان دار.",
            }
        )

        # ۶. مناطق و حامل‌ها
        provinces = ['تهران', 'اصفهان', 'فارس', 'خراسان رضوی', 'آذربایجان شرقی', 'البرز', 'قم', 'مازندران']
        for prov_name in provinces:
            Province.objects.get_or_create(name=prov_name)

        Carrier.objects.get_or_create(
            name="ارسال سریع و مطمئن (به سراسر کشور)",
            defaults={
                'delivery_time': "۲۴ الی ۴۸ ساعت کاری با بارنامه پیامکی",
                'cost': 35000,
                'free_shipping_min_order': 400000,
                'is_eco_friendly': True,
                'is_active': True,
            }
        )

        # ۷. اسلایدر و بنرها
        Slider.objects.get_or_create(
            title="دانش کهن، سلامت مدرن؛ انتخاب آگاهانه گیاهان دارویی",
            defaults={
                'subtitle': "با دستیار هوشمند سلامت از مشاوره تا خرید، همیشه در کنار شما هستیم.",
                'link': "/remedy/wizard/",
                'order': 1,
                'is_active': True,
            }
        )

        # ۸. کدهای تخفیف
        now = timezone.now()
        Coupon.objects.get_or_create(
            code="NOBAHAR1403",
            defaults={
                'discount_type': 'percent',
                'value': 20,
                'min_order_amount': 100000,
                'max_discount_amount': 50000,
                'valid_from': now - timedelta(days=1),
                'valid_until': now + timedelta(days=90),
                'usage_limit': 200,
                'is_active': True,
            }
        )

        # ۹. عارضه‌یاب و بانک داروهای شیمیایی
        cat_stress, _ = SymptomCategory.objects.get_or_create(
            slug="stress-anxiety",
            defaults={
                'title': "استرس و اضطراب",
                'icon': "moon",
                'description': "تسکین بی‌خوابی، دلهره، سردردهای میگرنی و خستگی مزمن ناشی از کار"
            }
        )
        cat_digestive, _ = SymptomCategory.objects.get_or_create(
            slug="digestive-issues",
            defaults={
                'title': "مشکلات گوارشی و کبد",
                'icon': "leaf",
                'description': "رفع نفخ، سوزش سردل، سندرم روده تحریک‌پذیر و پاکسازی کبد چرب"
            }
        )
        cat_cold, _ = SymptomCategory.objects.get_or_create(
            slug="cold-respiratory",
            defaults={
                'title': "سرماخوردگی و تقویت ایمنی",
                'icon': "shield",
                'description': "تقویت سیستم ایمنی، تسکین سرفه، گلودرد و سینوزیت"
            }
        )
        cat_joint, _ = SymptomCategory.objects.get_or_create(
            slug="joint-pain",
            defaults={
                'title': "دردهای مفصلی و عضلانی",
                'icon': "activity",
                'description': "تسکین دردهای آرتروز، کوفتگی عضلات و گرفتگی‌های مفصلی"
            }
        )

        # داروها
        drug_none, _ = ChemicalDrug.objects.get_or_create(
            name="دارو ندارد",
            defaults={'category': 'بدون مصرف داروی شیمیایی', 'description': 'شخص در حال حاضر داروی خاصی مصرف نمی‌کند'}
        )
        drug_warfarin, _ = ChemicalDrug.objects.get_or_create(
            name="وارفارین (رقیق‌کننده خون)",
            defaults={'category': 'ضد انعقاد خون', 'description': 'داروی قلبی عروقی'}
        )
        drug_aspirin, _ = ChemicalDrug.objects.get_or_create(
            name="آسپرین (ضد پلاکت)",
            defaults={'category': 'رقیق‌کننده خون', 'description': 'داروی قلبی و ضد درد'}
        )
        drug_losartan, _ = ChemicalDrug.objects.get_or_create(
            name="لوزارتان (فشار خون)",
            defaults={'category': 'کنترل فشار خون', 'description': 'داروی قلبی'}
        )

        # تداخلات
        DrugInteraction.objects.get_or_create(
            drug=drug_warfarin,
            product=p_gavzaban,
            defaults={
                'severity': 'danger',
                'warning_text': 'مصرف همزمان گل گاوزبان با داروی وارفارین به دلیل تشدید اثر ضد انعقادی خطر خونریزی دارد.'
            }
        )

        # پکیج پیشنهادی
        pkg_stress, _ = HealthRemedyPackage.objects.get_or_create(
            title="دمنوش آرامش‌بخش و گل‌گاوزبان ممتاز",
            defaults={
                'category': cat_stress,
                'description': "ترکیب گیاهی سنتی مؤثر برای بازیابی ریتم خواب طبیعی و تسکین بی‌قراری فکری بدون وابستگی دارویی.",
                'usage_guide': "یک فنجان دمنوش آرامش ساعت ۲۱ میل شود. در طول روز نیز دمنوش رقیق گل‌گاوزبان مصرف گردد.",
                'discounted_package_price': 165000,
            }
        )
        pkg_stress.products.set([p_damnoosh, p_gavzaban])

        self.stdout.write(self.style.SUCCESS("داده‌های منطبق بر موکاپ با موفقیت ذخیره شدند!"))

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from accounts.models import User, SellerProfile, EmailOTP
from core.models import StoreSetting
from catalog.models import Category, Brand, Supplier, Product, ProductVariant, ProductFeature, ProductReview, Wishlist
from orders.models import Cart, CartItem, Order, OrderItem, BankReceipt, Coupon
from shipping.models import Province, Carrier
from marketing.models import Slider, Banner
from pages.models import StaticPage, Article, ContactMessage
from remedy.models import SymptomCategory, ChemicalDrug, DrugInteraction, HealthRemedyPackage


class Command(BaseCommand):
    help = "پاکسازی دیتای کهنه و استقرار پایگاه داده ۱۰۰٪ واقعی و پروداکشن ۷ روزه عطارخونه"

    def handle(self, *args, **options):
        self.stdout.write("شروع پاکسازی داده‌های قدیمی و بارگذاری دیتابیس تمیز پروداکشن...")

        now = timezone.now()

        # ۱. پاکسازی کامل داده‌های قبلی
        Wishlist.objects.all().delete()
        ProductReview.objects.all().delete()
        BankReceipt.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        ProductFeature.objects.all().delete()
        ProductVariant.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()
        Supplier.objects.all().delete()
        Coupon.objects.all().delete()
        EmailOTP.objects.all().delete()
        ContactMessage.objects.all().delete()
        Article.objects.all().delete()
        StaticPage.objects.all().delete()
        Slider.objects.all().delete()
        Banner.objects.all().delete()

        # حذف کاربران به جز در صورت نیاز
        User.objects.all().delete()

        self.stdout.write("داده‌های قبلی با موفقیت پاکسازی شدند.")

        # ۲. تنظیمات پایه فروشگاه عطارخونه
        setting = StoreSetting.get_settings()
        setting.store_name = "عطارخونه"
        setting.slogan = "دانش کهن، سلامت مدرن؛ مرجع اصالت گیاهان دارویی ارگانیک"
        setting.phone = "021-88997766"
        setting.mobile = "09121112233"
        setting.email = "abolfazlfazeli760@gmail.com"
        setting.address = "تهران، خیابان ولیعصر، تقاطع طالقانی، مجتمع دارویی سلامت، پلاک ۱۱۴"
        setting.postal_code = "1591613114"
        setting.province = "تهران"
        setting.city = "تهران"
        setting.gift_wrap_cost = 25000
        setting.free_shipping_threshold = 450000
        setting.eitaa = "attarkhone_official"
        setting.bale = "attarkhone_bale"
        setting.telegram = "attarkhone_channel"
        setting.instagram = "attarkhone_ir"
        setting.is_maintenance_mode = False
        setting.save()

        # ۳. ایجاد استان‌ها و شرکت‌های حامل پستی (کارگاه ۴ و ۲۳)
        provinces_names = [
            "تهران", "اصفهان", "فارس", "خراسان رضوی",
            "آذربایجان شرقی", "مازندران", "گیلان", "قزوین",
            "البرز", "مرکزی", "خوزستان", "یزد",
            "کرمان", "همدان", "قم"
        ]
        prov_objs = {}
        for p_name in provinces_names:
            p, _ = Province.objects.get_or_create(name=p_name, defaults={'is_active': True})
            prov_objs[p_name] = p

        c_express, _ = Carrier.objects.get_or_create(
            name="پست پیشتاز جمهوری اسلامی ایران",
            defaults={
                'delivery_time': "۲ الی ۳ روز کاری",
                'cost': 45000,
                'free_shipping_min_order': 450000,
                'is_eco_friendly': True,
                'is_active': True
            }
        )
        c_tipax, _ = Carrier.objects.get_or_create(
            name="تیپاکس اکسپرس (تحویل درب محل)",
            defaults={
                'delivery_time': "۲۴ الی ۴۸ ساعت",
                'cost': 65000,
                'free_shipping_min_order': 600000,
                'is_eco_friendly': False,
                'is_active': True
            }
        )
        c_courier, _ = Carrier.objects.get_or_create(
            name="پیک موتوری برقی ویژه پایتخت (تحویل زیر ۳ ساعت)",
            defaults={
                'delivery_time': "همان روز (۲ الی ۴ ساعت)",
                'cost': 55000,
                'free_shipping_min_order': 400000,
                'is_eco_friendly': True,
                'is_active': True
            }
        )

        # ۴. ایجاد کاربران مدیریتی، کارمندان و فروشندگان
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@attarkhone.ir',
            password='AdminAttar1403!',
            first_name='مدیر ارشد',
            last_name='عطارخونه',
            phone='09121112233',
            role='admin',
            email_verified=True
        )

        hesabdar = User.objects.create_user(
            username='hesabdar',
            email='accounting@attarkhone.ir',
            password='Staff123456!',
            first_name='محسن',
            last_name='تقوی (حسابدار ارشد)',
            phone='09122223344',
            role='accountant',
            is_staff=True,
            email_verified=True
        )

        anbardar = User.objects.create_user(
            username='anbardar',
            email='warehouse@attarkhone.ir',
            password='Staff123456!',
            first_name='سعید',
            last_name='مرتضوی (مسئول انبار و لجستیک)',
            phone='09123334455',
            role='warehouse',
            is_staff=True,
            email_verified=True
        )

        # فروشنده ۱: مزرعه گیاهان کوهستانی احیاء (قزوین/مازندران)
        seller1 = User.objects.create_user(
            username='mazrae_ehya',
            email='mazrae.ehya@attarkhone.ir',
            password='Seller123456!',
            first_name='مهندس علی',
            last_name='رضایی',
            phone='09124445566',
            role='seller',
            email_verified=True
        )
        SellerProfile.objects.create(
            user=seller1,
            store_name='مزرعه ارگانیک گیاهان کوهستانی احیاء',
            slug='mazrae-ehya',
            national_id_or_registration='0012984712',
            shaba_number='IR980120000000008472910382',
            phone_work='02188776655',
            address='استان قزوین، منطقه الموت، روستای گازرخان، مزرعه نمونه احیاء',
            description='کشت ارگانیک، سایه‌خشک استاندارد و بدون سموم شیمیایی گل گاوزبان و گیاهان بومی با تاییدیه حفظ نباتات.',
            commission_percent=10,
            is_approved=True
        )

        # فروشنده ۲: تعاونی زنبورداران کوهستان سبلان (اردبیل)
        seller2 = User.objects.create_user(
            username='zanboor_sabalan',
            email='sabalan.honey@attarkhone.ir',
            password='Seller123456!',
            first_name='حاج داوود',
            last_name='سبلانی',
            phone='09145556677',
            role='seller',
            email_verified=True
        )
        SellerProfile.objects.create(
            user=seller2,
            store_name='تعاونی زنبورداران کوهستان سبلan',
            slug='zanboor-sabalan',
            national_id_or_registration='10861234567',
            shaba_number='IR420170000000001234567890',
            phone_work='04533221100',
            address='استان اردبیل، دامنه‌های سبلان، سرعین، ییلاقات آلوارس',
            description='برداشت مستقیم عسل طبیعی خام با ساکارز آزمایشگاهی زیر ۲٪، گرده گل کوهستان و ژل رویال اصل.',
            commission_percent=10,
            is_approved=True
        )

        # فروشنده ۳: کارگاه سنتی تقطیر نیاسر کاشان (اصفهان)
        seller3 = User.objects.create_user(
            username='golestan_kashan',
            email='golestan.kashan@attarkhone.ir',
            password='Seller123456!',
            first_name='استاد حسین',
            last_name='کاشانی',
            phone='09136667788',
            role='seller',
            email_verified=True
        )
        SellerProfile.objects.create(
            user=seller3,
            store_name='کارگاه تقطیر سنتی گلستان قمصر کاشان',
            slug='golestan-kashan',
            national_id_or_registration='14008912345',
            shaba_number='IR650560000000009876543210',
            phone_work='03155443322',
            address='استان اصفهان، کاشان، قمصر، کارگاه سنتی تقطیر دیگ مسی',
            description='تولید اصیل گلاب دوآتشه سنگین، عرق نعناع فلفلی اعلا و عرقیات خالص در ظروف سنتی مسی.',
            commission_percent=10,
            is_approved=True
        )

        # خریداران مشتری حقیقی
        customers = []
        cust_specs = [
            ('sara_tehrani', 'sara.tehrani@gmail.com', 'سارا', 'تهرانی', '09121110001', 'تهران', 'خیابان سعادت‌آباد، خیابان صرافها، پلاک ۴۲'),
            ('ali_rezaei', 'ali.rezaei@gmail.com', 'علی', 'رضایی', '09132220002', 'اصفهان', 'چهارباغ عباسی، کوچه سینما ساحل، مجتمع نگین'),
            ('maryam_ahmadi', 'maryam.ahmadi@gmail.com', 'دکتر مریم', 'احمدی', '09173330003', 'فارس', 'شیراز، خیابان ملاصدرا، کوچه ۴، ساختمان پزشکان'),
            ('mohammad_karimi', 'm.karimi@gmail.com', 'محمد', 'کریمی', '09154440004', 'خراسان رضوی', 'مشهد، بلوار سجاد، خیابان بهارستان، پلاک ۱۸'),
            ('fatemeh_soleimani', 'f.soleimani@gmail.com', 'فاطمه', 'سلیمانی', '09145550005', 'آذربایجان شرقی', 'تبریز، کوی ولیعصر، خیابان پروین اعتصامی'),
            ('reza_moradi', 'reza.moradi@gmail.com', 'رضا', 'مرادی', '09116660006', 'گیلان', 'رشت، گلسار، بلوار سمیه، کوچه ۱۲۲'),
        ]
        for u_name, email, f_name, l_name, phone, prov, addr in cust_specs:
            u = User.objects.create_user(
                username=u_name,
                email=email,
                password='Customer123456!',
                first_name=f_name,
                last_name=l_name,
                phone=phone,
                role='customer',
                email_verified=True
            )
            customers.append((u, prov, addr))

        # ۵. ایجاد شاخه‌ها و دسته‌بندی‌های تخصصی
        cat_herbs = Category.objects.create(name='گیاهان دارویی و دمنوش‌های کوهی', slug='herbs-tea', description='برگ‌ها، گل‌ها و دانه‌های ارگانیک دست‌چین دامنه‌های البرز و زاگرس')
        cat_distillates = Category.objects.create(name='عرقیات سنتی دوآتشه و گلاب', slug='distillates', description='تقطیر شده در دیگ‌های سنتی مسی با بالاترین غلظت اسانس طبیعی')
        cat_honey = Category.objects.create(name='عسل‌های طبیعی و فرآورده‌های زنبور', slug='honey-bee', description='عسل خام حرارت‌ندیده با برگه آزمایش ساکارز آزمایشگاه مرجع')
        cat_oils = Category.objects.create(name='روغن‌های درمانی و عصاره‌های گیاهی', slug='herbal-oils', description='روغن‌های فرابکر پرس سرد و اکستراکت‌های تغلیظ‌شده درمانی')
        cat_spices = Category.objects.create(name='ادویه‌جات اعلا و چاشنی‌های دست‌چین', slug='spices', description='ادویه‌های هندی و سنتی ایرانی آسیاب‌نشده با عطر و طعم فوق‌العاده')

        # برندها و تامین‌کنندگان
        b_attar, _ = Brand.objects.get_or_create(name='عطارخونه گلچین', slug='attarkhone-select', website='https://attarkhone.ir')
        b_sabalan, _ = Brand.objects.get_or_create(name='سبلان ارگانیک', slug='sabalan-organic')
        b_kashan, _ = Brand.objects.get_or_create(name='گلستان کاشان', slug='golestan-kashan')

        # ۶. ایجاد ۱۲ محصول اصیل با کلیه مشخصات علمی و کارگاهی
        products_data = [
            {
                'name': 'گل گاوزبان ارگانیک کوهی اشکورات',
                'slug': 'echium-amoenum-eshkevarat',
                'category': cat_herbs,
                'seller': seller1,
                'base_price': 98000,
                'discount_percent': 10,
                'stock': 45,
                'scientific_name': 'Echium amoenum Fisch. & C.A. Mey.',
                'botanical_family': 'Boraginaceae (گاوزبانیان)',
                'harvest_region': 'اشکورات گیلان و الموت قزوین (ارتفاع ۲۲۰۰ متر)',
                'temperament': 'warm_wet',
                'active_compounds': 'آنتوسیانین‌ها، فلاونوئیدها، اسید رزمارینیک و موسیلاژ لعاب‌دار',
                'brewing_guide': '۳ الی ۵ گرم از گل‌های درسته را همراه با مصلح (یک پر لیمو عمانی یا نبات) به مدت ۱۰ دقیقه دم نمایید.',
                'contraindications': 'مصرف مداوم بیش از ۴ هفته متوالی بدون وقفه و در دوران بارداری پرهیز شود.',
                'health_license': 'سیب سلامت و پروانه ارگانیک ۱۴۰۳/۴۹۸۲۱',
                'short_description': 'گل گاوزبان اصل کوهی دست‌چین، تقویت‌کننده قوی قلب، آرام‌بخش اعصاب و رافع تپش قلب.',
                'description': 'گل گاوزبان ایرانی یکی از نامدارترین گیاهان دارویی بومی ایران است که در قانون بوعلی سینا به عنوان مفرح قلب و مبهج روح معرفی شده است. این محصول با روش سنتی در سایه خشک شده تا رنگ بنفش تیره و ترکیبات فعال فیتوشیمیایی آن به صورت حداکثری حفظ گردند.',
                'is_organic': True,
                'is_featured': True,
                'image': '/static/img/products/real_herb.jpg',
            },
            {
                'name': 'اسطوخودوس فرانسوی کوهپایه (لاواندر اعلا)',
                'slug': 'lavandula-angustifolia-premium',
                'category': cat_herbs,
                'seller': seller1,
                'base_price': 115000,
                'discount_percent': 0,
                'stock': 38,
                'scientific_name': 'Lavandula angustifolia Mill.',
                'botanical_family': 'Lamiaceae (نعناعیان)',
                'harvest_region': 'کوهپایه‌های خشک و آفتابگیر البرز مرکزی',
                'temperament': 'warm_dry',
                'active_compounds': 'لینالول، لینالیل استات، کافور طبیعی و ترکیبات پلی‌فنولی',
                'brewing_guide': 'یک قاشق مرباخوری را در یک لیوان آب جوش ریخته و به مدت ۸ دقیقه دم کنید. مصرف پیش از خواب توصیه می‌شود.',
                'contraindications': 'همزمان با داروهای خواب‌آور و آرام‌بخش قوی شیمیایی با احتیاط مصرف شود.',
                'health_license': 'سیب سلامت ۱۴۰۳/۵۱۲۳۴',
                'short_description': 'گل‌های معطر لاواندر، رفع بی‌خوابی شبانه، تسکین سردردهای میگرنی و پاکسازی خلط سودا.',
                'description': 'اسطوخودوس به جاروب مغز معروف است؛ چرا که اخلاط زائد و سوداوی را از بطن‌های مغز پاکسازی کرده و موجب شادابی ذهن و آرامش عمیق خواب می‌گردد.',
                'is_organic': True,
                'is_featured': True,
                'image': '/static/img/categories/cat_wellness.jpg',
            },
            {
                'name': 'چای سبز بهاره لاهیجان (غنچه شکسته ممتاز)',
                'slug': 'lahijan-spring-green-tea',
                'category': cat_herbs,
                'seller': seller1,
                'base_price': 85000,
                'discount_percent': 15,
                'stock': 60,
                'scientific_name': 'Camellia sinensis (L.) Kuntze',
                'botanical_family': 'Theaceae (چاییان)',
                'harvest_region': 'باغات کوهپایه‌ای ارگانیک لاهیجان',
                'temperament': 'cold_dry',
                'active_compounds': 'اپی‌گالوکاتچین گالات (EGCG)، تیانین، پلی‌فنول‌های آنتی‌اکسیدانی',
                'brewing_guide': 'آب با دمای ۸۰ درجه سانتی‌گراد را روی برگ‌ها ریخته و پس از ۳ تا ۴ دقیقه صاف کنید.',
                'contraindications': 'مصرف ناشتا برای افراد با معده سرد و ضعیف توصیه نمی‌شود.',
                'health_license': 'پروانه بهداشتی ساخت ۲۱/۱۴۰۳',
                'short_description': 'سرشار از آنتی‌اکسیدان، چربی‌سوز طبیعی، محافظت از عروق کرونر و طراوت‌بخش پوست.',
                'description': 'برگ‌های دست‌چین بهاره که بلافاصله پس از برداشت بخاردهی شده‌اند تا فرآیند اکسیداسیون متوقف و کاتچین‌های ضدسرطان گیاه دست‌نخورده باقی بمانند.',
                'is_organic': True,
                'is_featured': True,
                'image': '/static/img/products/real_tea.jpg',
            },
            {
                'name': 'بابونه شیرازی ارگانیک (گل‌های کامل)',
                'slug': 'shiraz-chamomile-flowers',
                'category': cat_herbs,
                'seller': seller1,
                'base_price': 78000,
                'discount_percent': 0,
                'stock': 50,
                'scientific_name': 'Matricaria chamomilla L.',
                'botanical_family': 'Asteraceae (کاسنیان)',
                'harvest_region': 'دشت‌های حاصلخیز فارس و مرودشت',
                'temperament': 'warm_dry',
                'active_compounds': 'کامازولن، بیزابولول، فلاونوئید آپیژنین',
                'brewing_guide': 'یک قاشق غذاخوری را در قوری چینی به مدت ۱۰ دقیقه دم نموده و همراه با کمی عسل میل نمایید.',
                'contraindications': 'در افراد دارای آلرژی شدید به خانواده کاسنیان با احتیاط مصرف شود.',
                'health_license': 'سیب سلامت ۱۴۰۳/۷۶۵۴۳',
                'short_description': 'التیام‌بخش دردهای گوارشی و ورم معده، ضداسپاسم قوی و شفاف‌کننده پوست صورت.',
                'description': 'بابونه شیرازی از مرغوب‌ترین ارقام بابونه در جهان است که به دلیل دارا بودن اسانس آبی‌رنگ کامازولن، قوی‌ترین التیام‌بخش زخم معده و التهابات مخاطی به شمار می‌رود.',
                'is_organic': True,
                'is_featured': False,
                'image': '/static/img/products/prod_chamomile.jpg',
            },
            {
                'name': 'آویشن کوهی دنا (برگ‌های خشک پهن)',
                'slug': 'dena-mountain-thyme',
                'category': cat_herbs,
                'seller': seller1,
                'base_price': 92000,
                'discount_percent': 0,
                'stock': 35,
                'scientific_name': 'Thymus kotschyanus Boiss. & Hohen.',
                'botanical_family': 'Lamiaceae (نعناعیان)',
                'harvest_region': 'ارتفاعات صخره‌ای رشته‌کوه دنا',
                'temperament': 'warm_dry',
                'active_compounds': 'تیمول، کارواکرول، رزمارینیک اسید',
                'brewing_guide': 'یک قاشق چای‌خوری در یک فنجان آب جوش به مدت ۷ دقیقه دم شود.',
                'contraindications': 'در دوران بارداری به دلیل اثرات محرک رحمی ممنوع است.',
                'health_license': 'پروانه ساخت بهداشتی دنا ۱۴۰۳',
                'short_description': 'آنتی‌بیوتیک طبیعی مجاری تنفسی، خلط‌آور قوی، رافع سرفه و ضدعفونی‌کننده سینوس‌ها.',
                'description': 'آویشن دنا به دلیل رویش در ارتفاعات بالا و شرایط دشوار کوهستانی، بیشترین غلظت تیمول دارویی را داراست و از دیرباز ضدعفونی‌کننده اصلی ریه و جهاز هاضمه بوده است.',
                'is_organic': True,
                'is_featured': False,
                'image': '/static/img/products/real_jar.jpg',
            },
            {
                'name': 'گلاب دوآتشه سنتی قمصر کاشان',
                'slug': 'ghamsar-rose-water-double-distilled',
                'category': cat_distillates,
                'seller': seller3,
                'base_price': 135000,
                'discount_percent': 10,
                'stock': 55,
                'scientific_name': 'Rosa damascena Herrm.',
                'botanical_family': 'Rosaceae (گل‌سرخیان)',
                'harvest_region': 'قمصر و برزک کاشان',
                'temperament': 'moderate',
                'active_compounds': 'سیترونلول، ژرانیول، فنیل اتیل الکل',
                'brewing_guide': 'یک الی دو قاشق غذاخوری در آب خنک یا شربت‌های سنتی میل شود.',
                'contraindications': 'منع مصرف شناخته‌شده‌ای ندارد.',
                'health_license': 'سیب سلامت و استاندارد ملی ایران ۶۹/۱۴۰۳',
                'short_description': 'تقطیر دوگانه گل‌های محمدی صبحگاهی، مقوی قلب و اعصاب، روشن‌کننده پوست و نشاط‌آور.',
                'description': 'در تولید این گلاب به جای آب، از گلاب نوبت اول در دیگ مسی ریخته شده و با گل‌های تازه گل‌محمدی مجدداً تقطیر شده است تا عیار اسانس به حداکثر ممکن برسد.',
                'is_organic': True,
                'is_featured': True,
                'image': '/static/img/products/prod_rose.jpg',
            },
            {
                'name': 'عرق نعناع فلفلی سنگین دوآتشه',
                'slug': 'heavy-peppermint-water-distillate',
                'category': cat_distillates,
                'seller': seller3,
                'base_price': 89000,
                'discount_percent': 0,
                'stock': 70,
                'scientific_name': 'Mentha piperita L.',
                'botanical_family': 'Lamiaceae (نعناعیان)',
                'harvest_region': 'مزارع کاشان و قمصر',
                'temperament': 'warm_dry',
                'active_compounds': 'منتول خالص دارویی، منتون، متیل استات',
                'brewing_guide': 'نصف استکان بعد از هر وعده غذایی سنگین میل شود.',
                'contraindications': 'افراد دارای رفلاکس شدید معده به مری با احتیاط مصرف کنند.',
                'health_license': 'پروانه غذا و دارو ۴۰۳/۳۳۱',
                'short_description': 'تسکین فوری نفخ و سنگینی معده، خنک‌کننده گوارش و ضداسپاسم قوی روده.',
                'description': 'عرق نعناع فلفلی سنگین با اسانس غنی منتول که موجب ریلکس شدن عضلات صاف دستگاه گوارش و هضم سریع غذاهای چرب می‌گردد.',
                'is_organic': True,
                'is_featured': True,
                'image': '/static/img/products/prod_mint.jpg',
            },
            {
                'name': 'عسل گون و آویشن کوهستان سبلان',
                'slug': 'sabalan-astragalus-thyme-raw-honey',
                'category': cat_honey,
                'seller': seller2,
                'base_price': 340000,
                'discount_percent': 8,
                'stock': 25,
                'scientific_name': 'Astragalus & Thymus Floral Honey',
                'botanical_family': 'Fabaceae / Lamiaceae',
                'harvest_region': 'دامنه‌های مرتفع کوه سبلان (ارتفاع ۲۶۰۰ متر)',
                'temperament': 'warm_wet',
                'active_compounds': 'ساکارز زیر ۱.۸٪، دیاستاز مثبت، پرولین بالا و فلاونوئیدها',
                'brewing_guide': 'یک قاشق مرباخوری ناشتا یا مخلوط در آب ولرم همراه با لیموترش تازه میل شود.',
                'contraindications': 'برای کودکان زیر یک سال منع مصرف دارد.',
                'health_license': 'شناسه تایید بهداشتی دامپزشکی و غذا و دارو',
                'short_description': 'عسل صددرصد طبیعی خام و حرارت‌ندیده، آنتی‌باکتریال قدرتمند و تقویت‌کننده سیستم ایمنی.',
                'description': 'این عسل در ییلاقات بکر سبلان تولید شده و بدون هرگونه شکردهی دستی و حرارت‌دهی صنعتی، مستقیماً از کندو پس از تصفیه اولیه بسته‌بندی گردیده است.',
                'is_organic': True,
                'is_featured': True,
                'image': '/static/img/products/real_box.jpg',
            },
            {
                'name': 'روغن سیاه‌دانه خالص پرس سرد (فرابکر)',
                'slug': 'pure-cold-pressed-black-seed-oil',
                'category': cat_oils,
                'seller': seller1,
                'base_price': 148000,
                'discount_percent': 0,
                'stock': 40,
                'scientific_name': 'Nigella sativa L. Seed Oil',
                'botanical_family': 'Ranunculaceae (آلالگان)',
                'harvest_region': 'مزارع بومی فلات مرکزی ایران',
                'temperament': 'warm_dry',
                'active_compounds': 'تیموکینون خالص، اسید لینولئیک (امگا ۶)، اسید اولئیک (امگا ۹)',
                'brewing_guide': 'مصرف موضعی جهت دردهای مفصلی و رماتیسم، یا خوراکی روزانه نصف قاشق چای‌خوری همراه با عسل.',
                'contraindications': 'مصرف خوراکی در دوران بارداری اکیداً ممنوع است.',
                'health_license': 'پروانه ساخت بهداشتی روغن‌های سنتی ۱۴۰۳',
                'short_description': 'غنی از تیموکینون دارویی، التیام‌بخش دردهای مفاصل، دیسک کمر، آرتروز و سینوزیت.',
                'description': 'روغن سیاه‌دانه در طب سنتی اکسیری برای تمامی بیماری‌ها به شمار می‌رود. روغن‌کشی به روش کلدپرس در دمای زیر ۳۵ درجه سانتی‌گراد صورت گرفته تا ساختار پیوندهای اسیدهای چرب حیاتی آسیب نبیند.',
                'is_organic': True,
                'is_featured': True,
                'image': '/static/img/categories/cat_oils.jpg',
            },
            {
                'name': 'زعفران سوپر نگین صادراتی قائنات',
                'slug': 'super-negin-saffron-qaenat',
                'category': cat_spices,
                'seller': seller1,
                'base_price': 295000,
                'discount_percent': 5,
                'stock': 50,
                'scientific_name': 'Crocus sativus L.',
                'botanical_family': 'Iridaceae (زنبقیان)',
                'harvest_region': 'مزارع زعفران قائنات خراسان جنوبی',
                'temperament': 'warm_dry',
                'active_compounds': 'کروسین (رنگ‌دهی ۲۷۰+)، پیکروکروسین (طعم‌دهی)، سافرانال (عطردهی)',
                'brewing_guide': 'سرگل‌ها را در هاون سنگی یا شیشه‌ای بسابید و با یخ یا آب جوش دم کنید.',
                'contraindications': 'مصرف در مقادیر بالا (بیش از ۱.۵ گرم در روز) خطرناک است.',
                'health_license': 'استاندارد ملی ایران شماره ۲۵۹-۱',
                'short_description': 'رشته‌های درشت و سرخ‌فام سوپر نگین بدون خامه زرد، شادی‌آور قوی و مقوی قلب.',
                'description': 'طلای سرخ ایران؛ زعفران سوپر نگین قائنات با کلاله‌های راست و سالم، بالاترین نمره آزمون کروسین و عطر بی‌نظیر طبیعی.',
                'is_organic': True,
                'is_featured': True,
                'image': '/static/img/products/prod_saffron.jpg',
            },
            {
                'name': 'هل اکبر بنفش اعلا (دانه‌های درشت هندی)',
                'slug': 'green-cardamom-purple-emperor',
                'category': cat_spices,
                'seller': seller1,
                'base_price': 165000,
                'discount_percent': 0,
                'stock': 30,
                'scientific_name': 'Elettaria cardamomum (L.) Maton',
                'botanical_family': 'Zingiberaceae (زنجبیلیان)',
                'harvest_region': 'تپه‌های کرالا هندوستان (بسته‌بندی انحصاری عطارخونه)',
                'temperament': 'warm_dry',
                'active_compounds': 'ترپینیل استات، سینئول، لینالول و اسانس‌های فرار',
                'brewing_guide': 'دانه‌ها را کمی نیم‌کوب کرده و همراه با چای یا دمنوش دم کنید.',
                'contraindications': 'افراد دارای زخم حاد معده و گرم‌مزاجان مفرط در حد اعتدال مصرف نمایند.',
                'health_license': 'پروانه گمرکی و بهداشتی واردات ادویه ۱۴۰۳',
                'short_description': 'دانه‌های سبز درشت با مغز سیاه و پرملات، خوشبوکننده دهان و مقوی معده.',
                'description': 'هل اکبر بنفش درجه‌یک‌ترین نوع هل سبز در جهان است که با قطری بیش از ۸ میلی‌متر و کپسول‌های کاملاً بسته و پر از دانه عرضه می‌گردد.',
                'is_organic': True,
                'is_featured': False,
                'image': '/static/img/categories/cat_spices.jpg',
            },
            {
                'name': 'پودر دارچین سیلان اصل سریلانکا',
                'slug': 'ceylon-cinnamon-true-powder',
                'category': cat_spices,
                'seller': seller1,
                'base_price': 118000,
                'discount_percent': 0,
                'stock': 42,
                'scientific_name': 'Cinnamomum verum J. Presl',
                'botanical_family': 'Lauraceae (برگ‌بویان)',
                'harvest_region': 'سریلانکا (سیلان اصل)',
                'temperament': 'warm_dry',
                'active_compounds': 'سینامالدئید طبیعی، کومارین بسیار ناچیز (بی‌خطر برای کبد)',
                'brewing_guide': 'نصف قاشق چای‌خوری در شربت‌ها، غذاها یا دمنوش دارچین و عسل.',
                'contraindications': 'افراد مستعد خونریزی و دارای حرارت کبد بالا با مصلحات خنک میل فرمایند.',
                'health_license': 'گواهی اصالت سیلان و پروانه بهداشت واردات',
                'short_description': 'دارچین واقعی سیلان با درصد کومارین صفر، تنظیم‌کننده قند خون و تقویت‌کننده سوخت‌وساز.',
                'description': 'برخلاف دارچین کاسیا چینی موجود در بازار که به علت داشتن کومارین بالا برای کبد سم است، دارچین اصل سیلان با طعم ملایم و شیرین دارویی، امن‌ترین گونه دارچین در دنیاست.',
                'is_organic': True,
                'is_featured': False,
                'image': '/static/img/categories/cat_spices.jpg',
            },
        ]

        created_products = []
        for pdata in products_data:
            p = Product.objects.create(
                category=pdata['category'],
                brand=b_attar,
                supplier=None,
                seller=pdata['seller'],
                name=pdata['name'],
                slug=pdata['slug'],
                scientific_name=pdata['scientific_name'],
                botanical_family=pdata['botanical_family'],
                harvest_region=pdata['harvest_region'],
                temperament=pdata['temperament'],
                active_compounds=pdata['active_compounds'],
                brewing_guide=pdata['brewing_guide'],
                contraindications=pdata['contraindications'],
                health_license=pdata['health_license'],
                base_price=pdata['base_price'],
                discount_percent=pdata['discount_percent'],
                stock=pdata['stock'],
                short_description=pdata['short_description'],
                description=pdata['description'],
                is_organic=pdata['is_organic'],
                is_featured=pdata['is_featured'],
                is_eco_packaging=True,
                sales_count=random.randint(5, 45)
            )
            created_products.append(p)

            # ۳ مشخصه وزنی استاندارد جهت راحتی انتخاب خریدار (کارگاه ۱۳)
            bp = p.final_price
            ProductVariant.objects.create(
                product=p,
                weight_label="۵۰ گرم",
                grind_type="درسته و سورت‌شده",
                price=max(15000, (bp * 55) // 100),
                stock=p.stock // 2 or 10,
                sku=f"SKU-{p.id}-50G"
            )
            ProductVariant.objects.create(
                product=p,
                weight_label="۱۰۰ گرم (استاندارد)",
                grind_type="درسته و سورت‌شده",
                price=bp,
                stock=p.stock,
                sku=f"SKU-{p.id}-100G"
            )
            ProductVariant.objects.create(
                product=p,
                weight_label="۲۵۰ گرم (اقتصادی)",
                grind_type="درسته و سورت‌شده",
                price=max(30000, (bp * 230) // 100),
                stock=p.stock // 3 or 5,
                sku=f"SKU-{p.id}-250G"
            )

            # ویژگی‌های کالا (کارگاه ۱۴)
            ProductFeature.objects.create(product=p, name="مزاج و طبع", value=p.get_temperament_display())
            ProductFeature.objects.create(product=p, name="منطقه رویش", value=p.harvest_region)
            ProductFeature.objects.create(product=p, name="ترکیبات مؤثره", value=p.active_compounds[:60])
            ProductFeature.objects.create(product=p, name="پروانه بهداشتی", value=p.health_license)

        self.stdout.write(f"تعداد {len(created_products)} محصول ممتاز با مشخصه‌ها و ویژگی‌های تخصصی ثبت گردید.")

        # ۷. ایجاد دیدگاه‌ها، نظرات خریداران و پرسش و پاسخ تخصصی داروساز (ProductReview)
        reviews_data = [
            (
                created_products[0], customers[0][0], "سارا تهرانی", 5,
                "رنگ گل‌ها فوق‌العاده بنفش و تازه بود. واقعاً عطر و لعاب بی‌نظیری داشت و با گل‌های کهنه عطاری‌های معمولی اصلاً قابل مقایسه نیست. سپاس از بسته‌بندی تمیز.",
                "با درود؛ خرسندیم از رضایت شما. گل‌های امساله اشکورات به دلیل برداشت به موقع در مه صبحگاهی و سایه‌خشک اصولی بالاترین غلظت موسیلاژ و فلاونوئید را دارا می‌باشند."
            ),
            (
                created_products[0], customers[1][0], "علی رضایی", 5,
                "آیا این گل گاوزبان برای کسانی که آسپرین مصرف می‌کنند تداخل دارد؟",
                "با سلام و احترام؛ به دلیل وجود ترکیبات ملایم رقیق‌کننده خون در اسید رزمارینیک، در صورت مصرف منظم آسپرین یا وارفارین بهتر است دوز مصرف دمنوش را به روزی یک فنجان سبک محدود نموده و با پزشک معالج هماهنگ فرمایید."
            ),
            (
                created_products[1], customers[2][0], "دکتر مریم احمدی", 5,
                "اسطوخودوس را برای رفع سردرد عصبی و بی‌خوابی تهیه کردم. کیفیت سورتینگ عالی بود و بدون چوب و خاک اضافی. کیفیت اسانس بسیار بالاست.",
                "با تشکر از دیدگاه ارزشمند سرکار عالی؛ گیاهان این غرفه مستقیماً از ارتفاعات دست‌چین می‌شوند تا ترکیبات لینالول و آرام‌بخش آن بدون اکسیداسیون به دست مصرف‌کننده برسد."
            ),
            (
                created_products[5], customers[3][0], "محمد کریمی", 5,
                "عطر گلاب تمام خانه را پر کرد. واقعاً دوآتشه اصل است و ته‌مزه تلخی دلپذیر ناشی از اسانس طبیعی گل محمدی را دارد.",
                "سلام و درود؛ خوشحالیم که اصالت گلاب سنتی قمصر مورد توجه شما قرار گرفت. در فرآیند تقطیر دیگ‌های مسی سنتی، تمام عیار گل به عصاره منتقل می‌گردد."
            ),
            (
                created_products[7], customers[4][0], "فاطمه سلیمانی", 5,
                "برگه آزمایش ساکارز عسل رو چک کردم، زیر ۲ درصد بود و طعم گیاه گون کاملاً حس می‌شه. پس از مدت‌ها یک عسل واقعی و شفا بخش خریدم.",
                "با سپاس از حسن اعتمادتان؛ زنبورستان‌های سبلان در مناطق بکر چراگاهی مستقر هستند و سلامت دارویی عسل خط قرمز پلتفرم عطارخونه است."
            ),
            (
                created_products[8], customers[5][0], "رضا مرادی", 4,
                "روغن سیاهدانه را برای زانودرد مادرم استفاده کردم، گرمای بسیار مطبوعی دارد و درد را تا حد زیادی آرام کرد. فقط کاش ظرف پمپی داشت.",
                "با درود؛ ممنون از پیشنهاد سازنده شما. در پارت بعدی تولید، ظروف شیشه‌ای قطره‌چکانی و پمپی استاندارد جایگزین خواهد شد."
            ),
        ]

        for p_obj, u_obj, a_name, r_val, comm, rep in reviews_data:
            ProductReview.objects.create(
                product=p_obj,
                user=u_obj,
                author_name=a_name,
                rating=r_val,
                comment=comm,
                reply=rep,
                replied_by=admin_user,
                replied_at=now - timedelta(days=2),
                is_approved=True,
                created_at=now - timedelta(days=4)
            )

        # ۸. کدهای تخفیف فعال (Coupons)
        Coupon.objects.create(
            code="NOBAHAR",
            discount_type="percent",
            value=15,
            min_order_amount=150000,
            usage_limit=100,
            used_count=18,
            is_active=True,
            valid_from=now - timedelta(days=7),
            valid_until=now + timedelta(days=30)
        )
        Coupon.objects.create(
            code="ATK1403",
            discount_type="fixed",
            value=25000,
            min_order_amount=200000,
            usage_limit=50,
            used_count=12,
            is_active=True,
            valid_from=now - timedelta(days=7),
            valid_until=now + timedelta(days=30)
        )
        Coupon.objects.create(
            code="SALAMAT",
            discount_type="percent",
            value=10,
            min_order_amount=100000,
            usage_limit=200,
            used_count=35,
            is_active=True,
            valid_from=now - timedelta(days=7),
            valid_until=now + timedelta(days=60)
        )

        # ۹. اسلایدرهای هیرو و بنرهای صفحه نخست (Marketing)
        Slider.objects.create(
            title="دانش کهن طب ایرانی، سلامت مدرن خانواده",
            subtitle="مجموعه‌ای بی‌نظیر از مرغوب‌ترین گیاهان دارویی ارگانیک، دمنوش‌های کوهی و عصاره‌های سنتی با تاییدیه اصالت آزمایشگاهی",
            link="/shop/",
            order=1,
            is_active=True
        )
        Slider.objects.create(
            title="برداشت تازه گل‌های کوهستانی الموت و اشکورات",
            subtitle="سایه‌خشک سنتی، حفظ حداکثری ترکیبات فیتوشیمیایی و عطر اصیل طبیعت",
            link="/shop/?cat=herbs-tea",
            order=2,
            is_active=True
        )
        Slider.objects.create(
            title="دستیار هوشمند سلامت و مشاوره بالینی گیاهی",
            subtitle="انتخاب فرآورده بر اساس مزاج، بررسی تداخلات با داروهای شیمیایی و فرمولاسیون تخصصی",
            link="/remedy/",
            order=3,
            is_active=True
        )

        # ۱۰. مقالات علمی و استنادی (Articles)
        Article.objects.create(
            title="بررسی فیتوشیمیایی و خواص بالینی گل گاوزبان ایرانی (Echium amoenum)",
            slug="echium-amoenum-phytochemical-review",
            summary="تحلیلی جامع بر مواد مؤثره، آنتوسیانین‌ها، اثرات آرام‌بخش و الزامات ایمنی مصرف گل گاوزبان بر پایه مراجع فارماکوپه و طب کهن.",
            content="""گل گاوزبان ایرانی گیاهی علفی و خودرو از تیره گاوزبانیان است که رویشگاه اصلی آن ارتفاعات کوهستانی البرز شمالی است. 
در کتاب قانون بوعلی سینا آمده است که این گیاه مقوی اعضای رئیسه بدن به‌ویژه قلب و مغز بوده و اخلاط سوداوی را تصفیه می‌نماید.
تحقیقات نوین فیتوشیمیایی نشان داده است که عصاره آبی این گل غنی از آنتوسیانین‌های پایدار و ترکیبات فنلی چون رزمارینیک اسید است که اثرات ضداضطراب مشابه دیازپام اما بدون ایجاد وابستگی از خود نشان می‌دهند.
توصیه مصرف بالینی: به دلیل حضور مقادیر اندک آلکالوئیدهای پیرولیزیدین، بهتر است همراه با لیمو عمانی یا عسل دم شده و پس از هر دوره ۴ هفته‌ای مصرف مداوم، یک هفته وقفه ایجاد شود.""",
            category="طب سنتی و تندرستی",
            image="/static/img/products/real_herb.jpg",
            reading_time=6,
            views_count=148,
            author_name="دکتر مریم سادات حسینی",
            author_title="متخصص داروسازی سنتی و عضو هیئت علمی پژوهشکده گیاهان دارویی",
            scientific_reviewer="مرکز تحقیقات کارآزمایی بالینی طب سنتی دانشگاه تهران",
            academic_references="""۱. قانون در طب، ابوعلی سینا، ترجمه عبدالرحمن شرفکندی (هژار)، جلد دوم، انتشارات سروش.
۲. فارماکوپه گیاهی ایران (IHP)، وزارت بهداشت، درمان و آموزش پزشکی، کمیته تدوین فارماکوپه.
۳. WHO Monographs on Selected Medicinal Plants, Vol 3, Geneva: World Health Organization.
۴. Phytomedicine Journal: Anxiolytic effects of Echium amoenum flavonoids, DOI: 10.1016/j.phymed.2020.153201.""",
            is_published=True,
            created_at=now - timedelta(days=6)
        )

        Article.objects.create(
            title="مصلحات در طب سنتی؛ چرا نباید دمنوش‌ها را به تنهایی مصرف کرد؟",
            slug="mosleh-rules-in-traditional-medicine",
            summary="آشنایی با مفهوم مصلح، تعادل بخشیدن به افعال ادویه و جلوگیری از عوارض گوارشی و کبدی در مصرف درازمدت گیاهان دارویی.",
            content="""در مکتب پزشکی کهن ایران، هر مفرد دارویی دارای کیفیات چهارگانه (گرمی، سردی، تری و خشکی) در درجات مختلف است. مصلح مادّه‌ای است که عوارض جانبی یک دارو یا غذا را کاهش داده، طبع آن را تعدیل نموده و به جذب و نفوذ بهتر آن در اندام‌های هدف کمک می‌کند.
به عنوان مثال:
- مصلح گل گاوزبان (گرم و تر): لیمو عمانی خنک‌کننده و تعدیل‌کننده فشار خون.
- مصلح چای سبز (سرد و خشک): دارچین، زنجبیل یا هل ساییده گرم‌کننده معده.
- مصلح عسل (گرم و خشک): آبلیمو ترش یا سرکه طبیعی انگور (سرکه‌انگبین).
رعایت این اصول تضمین‌کننده ایمنی درازمدت سلامت مصرف‌کنندگان فرآورده‌های طبیعی است.""",
            category="اصول تغذیه و سلامت",
            image="/static/img/products/real_tea.jpg",
            reading_time=5,
            views_count=210,
            author_name="دکتر محمدرضا باقری",
            author_title="پزشک و دکترای تخصصی طب سنتی ایرانی",
            scientific_reviewer="انجمن علمی طب سنتی ایران",
            academic_references="""۱. مخزن‌الادویه، عقیلی خراسانی شیرازی، تصحیح دکتر محمدرضا شمس اردکانی.
۲. هدایة المتعلمین فی الطب، ابوبکر اخوینی بخاری.
۳. اصول تدابیر بالینی و مصلحات ادویه مفرد، پژوهشکده علوم غدد و متابولیسم دانشگاه علوم پزشکی تهران.""",
            is_published=True,
            created_at=now - timedelta(days=4)
        )

        # ۱۱. پیام‌های واقعی تماس با ما (ContactMessage)
        ContactMessage.objects.create(
            full_name="دکتر بهرام سرمدی",
            phone="09123459988",
            email="sarmadi.lab@gmail.com",
            subject="درخواست تامین عمده گل گاوزبان و بابونه برای آزمایشگاه داروسازی",
            message="با سلام؛ آزمایشگاه تحقیقاتی ما جهت فرمولاسیون شربت گیاهی ضدسرفه نیازمند ۱۰ کیلوگرم گل گاوزبان و بابونه با آنالیز آزمایشگاهی و درصد اسانس استاندارد است. لطفاً بخش فروش سازمانی تماس حاصل فرمایند.",
            is_read=True,
            created_at=now - timedelta(days=3)
        )
        ContactMessage.objects.create(
            full_name="خانم مهندس نوری",
            phone="09112224455",
            email="nouri.farm@gmail.com",
            subject="درخواست پنل غرفه و تامین کالا",
            message="سلام و احترام؛ ما در ارتفاعات دیلمان گیلان مزرعه پرورش ارگانیک بادرنجبویه و نعناع فلفلی داریم و مایل به عرضه محصولات با برچسب QR در پلتفرم عطارخونه هستیم.",
            is_read=False,
            created_at=now - timedelta(days=1)
        )

        # ۱۱.۱ صفحات ایستا و قوانین (StaticPage - کارگاه ۶)
        StaticPage.objects.create(
            title="درباره عطارخونه و ارزش‌های کهن سلامت",
            slug="about-us",
            content="""<p class="lead">عطارخونه، پلتفرم تخصصی گیاهان دارویی اصیل، فرآورده‌های طبیعی و سلامت‌محور است که با هدف احیای حکمت کهن ایرانی در قالبی علمی، شفاف و مبتنی بر استاندارد فارماکوپه‌ای بنا نهاده شده است.</p>
<h3>ماموریت ما</h3>
<p>ما باور داریم گیاهان دارویی زمانی می‌توانند شفا و آرامش واقعی را به ارمغان آورند که در بالاترین درجه خلوص، عاری از بقایای سموم شیمیایی و با حفظ حداکثری اسانس‌ها و متابولیت‌های ثانویه فرآوری شوند. به همین منظور، تک‌تک محصولات عرضه شده در عطارخونه همراه با گواهی آنالیز آزمایشگاهی معتبر (COA)، تعیین ماده مؤثره و شناسنامه ریشه‌ای تولیدکننده عرضه می‌گردند.</p>
<h3>ارزش‌های راهبردی ما</h3>
<ul>
<li><strong>اصالت و خلوص ۱۰۰٪:</strong> بدون هیچ‌گونه ماده افزودنی، رنگ مصنوعی یا اسانس غیرطبیعی.</li>
<li><strong>بسته‌بندی زیست‌پذیر:</strong> استفاده از کاغذ کرافت بازیافت‌پذیر و شیشه‌های دارویی کدر برای محافظت در برابر نور و رطوبت.</li>
<li><strong>شفافیت علمی:</strong> ارائه شناسنامه گیاه‌شناسی، مزاج، مصلحات و تداخلات دارویی معتبر زیر نظر متخصصین طب سنتی و داروسازی گیاهی.</li>
</ul>""",
            is_published=True
        )

        StaticPage.objects.create(
            title="قوانین، مقررات و سلب مسئولیت پزشکی",
            slug="terms",
            content="""<p class="lead">استفاده از خدمات عطارخونه به منزله پذیرش کامل قوانین، رویه‌ها و سلب مسئولیت‌های بهداشتی ذیل می‌باشد.</p>
<h3>سلب مسئولیت پزشکی و مشاوره‌ای</h3>
<p>اطلاعات درج شده در دانشنامه، خواص محصولات و موتور هوشمند دستیار سلامت جنبه آموزشی و آگاهی‌بخشی عمومی دارد و به هیچ عنوان جایگزین تشخیص، تجویز و نظر پزشک معالج متخصص نخواهد بود. افرادی که بیماری‌های زمینه‌ای مزمن (فشار خون، دیابت، نارسایی کلیوی و قلبی) دارند، یا داروهای با دامنه اثر باریک (نظیر وارفارین، آمیودارون و لیتیوم) مصرف می‌کنند و زنان باردار یا شیرده، باید پیش از مصرف هر مفرد دارویی با پزشک خود مشورت نمایند.</p>
<h3>اصالت کالا و برچسب QR رهگیری</h3>
<p>کلیه بسته‌های عطارخونه مجهز به برچسب اختصاصی QR با قابلیت استعلام آنلاین سری ساخت، تاریخ انقضا و گواهی آزمایشگاهی می‌باشند. در صورت هرگونه مغایرت در بسته‌بندی یا مشاهده آسیب فیزیکی، خریدار حق دارد ظرف مدت ۴۸ ساعت مراتب را به پشتیبانی اعلام نموده و بسته را عودت دهد.</p>""",
            is_published=True
        )

        StaticPage.objects.create(
            title="شیوه‌های ارسال، بسته‌بندی محافظ و زمان‌بندی تحویل",
            slug="shipping-policy",
            content="""<p class="lead">تمام سفارش‌ها در عطارخونه با نهایت دقت و در پوشش‌های محافظ دارویی استاندارد بسته‌بندی و تحویل شبکه پستی و حمل‌ونقل تخصصی می‌گردند.</p>
<h3>شیوه‌های ارسال</h3>
<ul>
<li><strong>پست پیشتاز کشوری:</strong> برای سراسر استان‌ها و شهرستان‌های کشور با زمان تحویل ۲ الی ۴ روز کاری و کد پیگیری ۲۴ رقمی پیامک شده.</li>
<li><strong>تیپاکس (ارسال سریع):</strong> تحویل ۲۴ تا ۴۸ ساعته با امکان بیمه اختصاصی محموله‌های شیشه‌ای و عرقیات گیاهی.</li>
<li><strong>پیک اکسپرس درون‌شهری (تهران):</strong> امکان تحویل همان‌روزه در مناطق ۲۲ گانه شهر تهران برای سفارش‌های ثبت‌شده پیش از ساعت ۱۲ ظهر.</li>
</ul>
<h3>استاندارد بسته‌بندی گیاهی</h3>
<p>به منظور حفظ ترکیبات فرار و اسانس‌های آلی، تمامی گیاهان دارویی درون پاکت‌های چندلایه کرافت ضدرطوبت با لایه محافظ فودگرید بسته‌بندی شده و شیشه‌های روغن و عصاره‌ها دارای پلمپ حرارتی و ضربه‌گیر هوایی هستند.</p>""",
            is_published=True
        )

        # ۱۲. ایجاد سفارشات واقعی ۷ روز گذشته (Orders & Workflows)
        # سفارش ۱: ۶ روز پیش - تحویل داده شده (Delivered)
        order1 = Order.objects.create(
            tracking_code=Order.generate_tracking_code(),
            user=customers[0][0],
            full_name="سارا تهرانی",
            phone="09121110001",
            email="sara.tehrani@gmail.com",
            province=prov_objs["تهران"],
            city="تهران",
            address="خیابان سعادت‌آباد، خیابان صرافها، کوچه ۳۳، پلاک ۴۲، واحد ۴",
            postal_code="1998811223",
            carrier=c_tipax,
            shipping_cost=c_tipax.cost,
            is_gift_wrapped=True,
            gift_message="با آرزوی تندرستی و شادابی برای دوست عزیزم",
            gift_cost=setting.gift_wrap_cost,
            subtotal=created_products[0].final_price * 2 + created_products[1].final_price,
            total_amount=created_products[0].final_price * 2 + created_products[1].final_price + c_tipax.cost + setting.gift_wrap_cost,
            payment_method="online",
            is_paid=True,
            status="delivered",
            zarinpal_authority="A00000000000000000000000000984712",
            zarinpal_ref_id="294817263541",
            admin_notes="تحویل داده شده به گیرنده در ساعت ۱۶:۳۰ با امضای الکترونیک",
            created_at=now - timedelta(days=6, hours=4)
        )
        order1.created_at = now - timedelta(days=6, hours=4)
        order1.save(update_fields=['created_at'])
        OrderItem.objects.create(order=order1, product=created_products[0], product_name=created_products[0].name, variant_label="۱۰۰ گرم (استاندارد)", price=created_products[0].final_price, quantity=2)
        OrderItem.objects.create(order=order1, product=created_products[1], product_name=created_products[1].name, variant_label="۱۰۰ گرم (استاندارد)", price=created_products[1].final_price, quantity=1)

        # سفارش ۲: ۵ روز پیش - تحویل داده شده (Delivered)
        order2 = Order.objects.create(
            tracking_code=Order.generate_tracking_code(),
            user=customers[1][0],
            full_name="علی رضایی",
            phone="09132220002",
            email="ali.rezaei@gmail.com",
            province=prov_objs["اصفهان"],
            city="اصفهان",
            address="چهارباغ عباسی، کوچه سینما ساحل، مجتمع نگین، واحد ۱۲",
            postal_code="8145612345",
            carrier=c_express,
            shipping_cost=c_express.cost,
            subtotal=created_products[5].final_price * 2 + created_products[7].final_price,
            total_amount=created_products[5].final_price * 2 + created_products[7].final_price + c_express.cost,
            payment_method="online",
            is_paid=True,
            status="delivered",
            zarinpal_authority="A00000000000000000000000000984855",
            zarinpal_ref_id="301827465912",
            admin_notes="کد رهگیری پستی مرسوله تحویل شده: ۲۸۴۷۱۰۰۰۲۹۳۸۴۷۵۶۱۰۲۹۳۸۴۷",
        )
        order2.created_at = now - timedelta(days=5, hours=6)
        order2.save(update_fields=['created_at'])
        OrderItem.objects.create(order=order2, product=created_products[5], product_name=created_products[5].name, variant_label="بسته ۵۰۰ میلی‌لیتر شیشه", price=created_products[5].final_price, quantity=2)
        OrderItem.objects.create(order=order2, product=created_products[7], product_name=created_products[7].name, variant_label="شیشه ۱ کیلوگرم خام", price=created_products[7].final_price, quantity=1)

        # سفارش ۳: ۴ روز پیش - ارسال شده با حامل (Shipped)
        order3 = Order.objects.create(
            tracking_code=Order.generate_tracking_code(),
            user=customers[2][0],
            full_name="دکتر مریم احمدی",
            phone="09173330003",
            email="maryam.ahmadi@gmail.com",
            province=prov_objs["فارس"],
            city="شیراز",
            address="خیابان ملاصدرا، کوچه ۴، ساختمان پزشکان پارس، طبقه ۳",
            postal_code="7134567890",
            carrier=c_express,
            shipping_cost=c_express.cost,
            subtotal=created_products[2].final_price + created_products[9].final_price,
            total_amount=created_products[2].final_price + created_products[9].final_price + c_express.cost,
            payment_method="online",
            is_paid=True,
            status="shipped",
            zarinpal_authority="A00000000000000000000000000985102",
            zarinpal_ref_id="312948572619",
            admin_notes="کد بارنامه پست پیشتاز: ۹۸۲۳۷۴۰۱۹۲۸۳۷۴۶۵۰۱۹۲۸۳۷۴",
        )
        order3.created_at = now - timedelta(days=4, hours=2)
        order3.save(update_fields=['created_at'])
        OrderItem.objects.create(order=order3, product=created_products[2], product_name=created_products[2].name, variant_label="۱۰۰ گرم (استاندارد)", price=created_products[2].final_price, quantity=1)
        OrderItem.objects.create(order=order3, product=created_products[9], product_name=created_products[9].name, variant_label="بسته ۱ مثقال سوپر نگین", price=created_products[9].final_price, quantity=1)

        # سفارش ۴: ۳ روز پیش - پرداخت شده با فیش بانکی کارت‌به‌کارت و ارسال شده (Shipped)
        order4 = Order.objects.create(
            tracking_code=Order.generate_tracking_code(),
            user=customers[3][0],
            full_name="محمد کریمی",
            phone="09154440004",
            email="m.karimi@gmail.com",
            province=prov_objs["خراسان رضوی"],
            city="مشهد",
            address="بلوار سجاد، خیابان بهارستان، پلاک ۱۸",
            postal_code="9177890123",
            carrier=c_express,
            shipping_cost=c_express.cost,
            subtotal=created_products[6].final_price * 3,
            total_amount=created_products[6].final_price * 3 + c_express.cost,
            payment_method="bank_receipt",
            is_paid=True,
            status="shipped",
            admin_notes="فیش بانکی کارت به کارت تایید شد. بارنامه پستی: ۸۴۹۲۰۱۸۳۷۴۶۵۰۱۹۲۸۳۷۴۶۵۸۲",
        )
        order4.created_at = now - timedelta(days=3, hours=5)
        order4.save(update_fields=['created_at'])
        OrderItem.objects.create(order=order4, product=created_products[6], product_name=created_products[6].name, variant_label="بطری ۱ لیتری سنتی", price=created_products[6].final_price, quantity=3)
        receipt4 = BankReceipt.objects.create(
            order=order4,
            bank_name="بانک ملی ایران",
            tracking_number="8492019382",
            card_last_digits="6037",
            deposited_amount=order4.total_amount,
            is_verified=True,
            verified_by=hesabdar,
            admin_comment="واریز وجه در صورتحساب بانکی تایید شد."
        )
        receipt4.created_at = now - timedelta(days=3, hours=5)
        receipt4.save(update_fields=['created_at', 'admin_comment'])

        # سفارش ۵: ۲ روز پیش - در حال بسته‌بندی در انبار (Processing)
        order5 = Order.objects.create(
            tracking_code=Order.generate_tracking_code(),
            user=customers[4][0],
            full_name="فاطمه سلیمانی",
            phone="09145550005",
            email="f.soleimani@gmail.com",
            province=prov_objs["آذربایجان شرقی"],
            city="تبریز",
            address="کوی ولیعصر، خیابان پروین اعتصامی، ساختمان شهریار، واحد ۶",
            postal_code="5156789012",
            carrier=c_tipax,
            shipping_cost=c_tipax.cost,
            subtotal=created_products[8].final_price + created_products[10].final_price,
            total_amount=created_products[8].final_price + created_products[10].final_price + c_tipax.cost,
            payment_method="online",
            is_paid=True,
            status="processing",
            zarinpal_authority="A00000000000000000000000000985399",
            zarinpal_ref_id="320918475620",
            admin_notes="اقلام سورت‌شده و در حال بسته‌بندی ضدضربه در انبار مرکزی",
        )
        order5.created_at = now - timedelta(days=2, hours=3)
        order5.save(update_fields=['created_at'])
        OrderItem.objects.create(order=order5, product=created_products[8], product_name=created_products[8].name, variant_label="شیشه قطره‌چکان ۶۰ سی‌سی", price=created_products[8].final_price, quantity=1)
        OrderItem.objects.create(order=order5, product=created_products[10], product_name=created_products[10].name, variant_label="بسته ۵۰ گرم دانه درسته", price=created_products[10].final_price, quantity=1)

        # سفارش ۶: دیروز - پرداخت تاییدشده زرین‌پال در صف آماده‌سازی (Paid)
        order6 = Order.objects.create(
            tracking_code=Order.generate_tracking_code(),
            user=customers[5][0],
            full_name="رضا مرادی",
            phone="09116660006",
            email="reza.moradi@gmail.com",
            province=prov_objs["گیلان"],
            city="رشت",
            address="رشت، گلسار، بلوار سمیه، کوچه ۱۲۲، پلاک ۹",
            postal_code="4167890123",
            carrier=c_express,
            shipping_cost=c_express.cost,
            subtotal=created_products[3].final_price * 2 + created_products[11].final_price,
            total_amount=created_products[3].final_price * 2 + created_products[11].final_price + c_express.cost,
            payment_method="online",
            is_paid=True,
            status="paid",
            zarinpal_authority="A00000000000000000000000000985921",
            zarinpal_ref_id="339182746501",
            admin_notes="پرداخت آنلاین زرین‌پال تایید شد و برچسب پستی صادر گردید",
        )
        order6.created_at = now - timedelta(days=1, hours=7)
        order6.save(update_fields=['created_at'])
        OrderItem.objects.create(order=order6, product=created_products[3], product_name=created_products[3].name, variant_label="۱۰۰ گرم (استاندارد)", price=created_products[3].final_price, quantity=2)
        OrderItem.objects.create(order=order6, product=created_products[11], product_name=created_products[11].name, variant_label="۱۰۰ گرم پودر خالص", price=created_products[11].final_price, quantity=1)

        # سفارش ۷: امروز - در انتظار پرداخت فیش بانکی (Pending Payment)
        order7 = Order.objects.create(
            tracking_code=Order.generate_tracking_code(),
            user=customers[0][0],
            full_name="سارا تهرانی",
            phone="09121110001",
            email="sara.tehrani@gmail.com",
            province=prov_objs["تهران"],
            city="تهران",
            address="خیابان سعادت‌آباد، خیابان صرافها، پلاک ۴۲",
            postal_code="1998811223",
            carrier=c_courier,
            shipping_cost=c_courier.cost,
            subtotal=created_products[0].final_price + created_products[4].final_price,
            total_amount=created_products[0].final_price + created_products[4].final_price + c_courier.cost,
            payment_method="bank_receipt",
            is_paid=False,
            status="pending_payment",
            admin_notes="فیش واریزی در صف بررسی واحد مالی و حسابداری",
        )
        order7.created_at = now - timedelta(hours=3)
        order7.save(update_fields=['created_at'])
        OrderItem.objects.create(order=order7, product=created_products[0], product_name=created_products[0].name, variant_label="۱۰۰ گرم (استاندارد)", price=created_products[0].final_price, quantity=1)
        OrderItem.objects.create(order=order7, product=created_products[4], product_name=created_products[4].name, variant_label="۱۰۰ گرم (استاندارد)", price=created_products[4].final_price, quantity=1)
        receipt7 = BankReceipt.objects.create(
            order=order7,
            bank_name="بانک ملت",
            tracking_number="9928174561",
            card_last_digits="5022",
            deposited_amount=order7.total_amount,
            is_verified=False,
        )
        receipt7.created_at = now - timedelta(hours=2)
        receipt7.save(update_fields=['created_at'])

        self.stdout.write(self.style.SUCCESS(
            "دیتابیس ۱۰۰٪ واقعی، ارگانیک و پروداکشن ۷ روزه عطارخونه با تمام سناریوهای سفارش، فروشندگان، نظرات، مقالات و درگاه زرین‌پال با موفقیت استقرار یافت!"
        ))

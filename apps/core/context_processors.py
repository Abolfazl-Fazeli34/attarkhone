from .models import StoreSetting


def store_context(request):
    """
    متغیرهای سراسری مورد نیاز در تمامی صفحات فروشگاه
    بهینه‌شده برای پاسخ‌دهی سریع بدون ایجاد رکوردهای تکراری در دیتابیس
    """
    try:
        setting = StoreSetting.get_settings()
    except Exception:
        setting = None

    # شمارش اقلام سبد خرید کاربر یا مهمان بدون ایجاد سبد خالی
    cart_items_count = 0
    try:
        from orders.models import Cart
        cart = None
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        elif request.session.session_key:
            cart = Cart.objects.filter(session_key=request.session.session_key).first()

        if cart:
            cart_items_count = sum(item.quantity for item in cart.items.all())
    except Exception:
        cart_items_count = 0

    # دسته‌های اصلی برای هدر و منوی ناوبری
    categories = []
    try:
        from catalog.models import Category
        categories = Category.objects.filter(parent=None)[:8]
    except Exception:
        pass

    # شمارش اقلام علاقه‌مندی کاربر
    wishlist_count = 0
    try:
        if request.user.is_authenticated:
            from catalog.models import Wishlist
            wishlist_count = Wishlist.objects.filter(user=request.user).count()
    except Exception:
        wishlist_count = 0

    return {
        'store_setting': setting,
        'cart_count': cart_items_count,
        'wishlist_count': wishlist_count,
        'nav_categories': categories,
    }

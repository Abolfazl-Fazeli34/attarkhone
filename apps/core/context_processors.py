from .models import StoreSetting


def store_context(request):
    """
    متغیرهای سراسری مورد نیاز در تمامی صفحات فروشگاه
    """
    try:
        setting = StoreSetting.get_settings()
    except Exception:
        setting = None

    # شمارش اقلام سبد خرید کاربر یا مهمان
    cart_items_count = 0
    try:
        from orders.views import get_or_create_cart
        cart = get_or_create_cart(request)
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

    return {
        'store_setting': setting,
        'cart_count': cart_items_count,
        'nav_categories': categories,
    }

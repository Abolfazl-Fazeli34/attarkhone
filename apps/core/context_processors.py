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
        from orders.models import Cart
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.save()
                session_key = request.session.session_key
            cart = Cart.objects.filter(session_key=session_key).first()

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

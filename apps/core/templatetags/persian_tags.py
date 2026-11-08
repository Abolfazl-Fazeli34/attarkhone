from django import template

register = template.Library()

PERSIAN_DIGITS = {
    '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
    '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
}


@register.filter(name='fa_digits')
def to_persian_digits(value):
    """تبدیل ارقام انگلیسی به ارقام زیبای فارسی"""
    if value is None:
        return ''
    val_str = str(value)
    for en, fa in PERSIAN_DIGITS.items():
        val_str = val_str.replace(en, fa)
    return val_str


@register.filter(name='toman')
def toman_format(value):
    """قالب‌بندی قیمت با جداکننده سه‌رقمی و پسوند تومان"""
    if value is None or value == '':
        return '۰ تومان'
    try:
        val_int = int(value)
        formatted = f"{val_int:,}"
        return f"{to_persian_digits(formatted)} تومان"
    except (ValueError, TypeError):
        return f"{to_persian_digits(value)} تومان"


@register.filter(name='multiply')
def multiply(value, arg):
    """ضرب دو مقدار در قالب‌های تمپلیت"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter(name='calculate_old_price')
def calculate_old_price(price, discount_percent):
    """محاسبه دقیق قیمت اولیه پیش از اعمال تخفیف برای خط زدن قیمت"""
    try:
        p = int(price)
        d = int(discount_percent)
        if 0 < d < 100:
            return round((p * 100) / (100 - d) / 1000) * 1000
        return p
    except (ValueError, TypeError):
        return price


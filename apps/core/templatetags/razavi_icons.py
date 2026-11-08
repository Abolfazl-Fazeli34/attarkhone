import json
import os
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

JSON_PATH = os.path.join(os.path.dirname(__file__), 'razavi_icons_data.json')
try:
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        ICON_REGISTRY = json.load(f)
except Exception:
    ICON_REGISTRY = {}

ALIASES = {
    'cart': 'shopping-cart-trolley',
    'shopping-cart': 'shopping-cart-trolley',
    'shop-cart': 'shopping-cart-trolley',
    'heart': 'heart',
    'wishlist': 'heart',
    'user': 'profile',
    'profile': 'profile',
    'search': 'search',
    'bell': 'bell',
    'star': 'star',
    'gift': 'gift',
    'shield': 'shield',
    'shield-check': 'security-shield-network',
    'truck': 'package',
    'box': 'box',
    'package': 'package',
    'clock': 'time-clock-circle',
    'time': 'time-clock-circle',
    'calendar': 'calendar',
    'phone': 'call',
    'call': 'call',
    'mail': 'email',
    'email': 'email',
    'map-pin': 'map-pin',
    'location': 'location',
    'trash': 'delete-bin-2',
    'trash-2': 'delete-bin-2',
    'delete': 'delete-bin-2',
    'check': 'check',
    'check-circle': 'check-circle',
    'check2': 'check2',
    'filter': 'filter',
    'edit': 'edit-pencil',
    'lock': 'lock',
    'unlock': 'unlock',
    'key': 'key',
    'refresh': 'refresh',
    'rotate-ccw': 'refresh',
    'credit-card': 'credit-card',
    'arrow-right': 'arrow-right',
    'arrow-left': 'arrow-left',
    'chevron-down': 'chevron-down',
    'chevron-up': 'chevron-up',
    'chevron-right': 'chevron-right',
    'chevron-left': 'chevron-left',
    'close': 'close',
    'x': 'close',
    'sparkles': 'sparkles',
    'award': 'award',
    'medal': 'medal',
    'receipt': 'receipt',
    'invoice': 'invoice',
    'leaf': 'sparkles',
    'tag': 'tag',
    'eye': 'eye',
    'share': 'share',
    'download': 'download',
}


@register.simple_tag
def razavi_icon(name, size=20, stroke_width=1.8, **kwargs):
    """
    رندر رسمی آیکون‌های وکتور ارگانیک Streamline Freehand (سبک پروژه razavi-lifestyle)
    استفاده: {% razavi_icon 'cart' size=22 class='my-icon' %}
    """
    key = str(name).strip().lower()
    actual_key = ALIASES.get(key, key)
    icon_data = ICON_REGISTRY.get(actual_key)

    custom_class = kwargs.get('class', kwargs.get('className', ''))
    fill = kwargs.get('fill', 'currentColor')
    stroke = kwargs.get('stroke', 'none' if fill != 'none' else 'currentColor')

    if not icon_data:
        # در صورت نبود نام خاص در رجیستری، از آیکون پیش‌فرض ستاره استفاده می‌شود
        icon_data = ICON_REGISTRY.get('star', {
            'viewBox': '0 0 24 24',
            'body': '<circle cx="12" cy="12" r="9" fill="currentColor"/>'
        })

    view_box = icon_data.get('viewBox', '0 0 24 24')
    body = icon_data.get('body', '')

    svg_html = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{view_box}" '
        f'width="{size}" height="{size}" '
        f'class="app-icon streamline-freehand {custom_class}" '
        f'fill="{fill}" '
        f'stroke="{stroke}" '
        f'stroke-width="{stroke_width}" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'style="display: inline-block; vertical-align: middle; flex-shrink: 0;">'
        f'{body}'
        f'</svg>'
    )
    return mark_safe(svg_html)

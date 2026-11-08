import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)


def send_welcome_email(user, request=None):
    """
    ارسال ایمیل خوش‌آمدگویی رسمی همراه با کد تخفیف به مشتری جدید
    """
    if not user.email:
        return False

    site_url = request.build_absolute_uri('/')[:-1] if request else 'http://127.0.0.1:8000'
    subject = 'به عطارخونه خوش آمدید | کد تخفیف ویژه اولین خرید شما'
    
    context = {
        'user': user,
        'site_url': site_url,
    }

    try:
        html_content = render_to_string('emails/welcome_email.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Welcome email successfully sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {e}")
        return False


def send_order_confirmation_email(order, request=None):
    """
    ارسال صورت‌حساب و تاییدیه ثبت سفارش با جزئیات اقلام و کد رهگیری
    """
    recipient_email = order.email or (order.user.email if order.user else None)
    if not recipient_email:
        recipient_email = settings.DEFAULT_FROM_EMAIL  # ارسال به ادمین جهت پیگیری

    site_url = request.build_absolute_uri('/')[:-1] if request else 'http://127.0.0.1:8000'
    subject = f'رسید و تاییدیه سفارش {order.tracking_code} | فروشگاه عطارخونه'

    context = {
        'order': order,
        'site_url': site_url,
    }

    try:
        html_content = render_to_string('emails/order_invoice_email.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
            bcc=[settings.DEFAULT_FROM_EMAIL] if recipient_email != settings.DEFAULT_FROM_EMAIL else None,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Order invoice email successfully sent to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send order email to {recipient_email}: {e}")
        return False


def send_consultation_confirmation_email(booking, request=None):
    """
    ارسال تاییدیه نوبت مشاوره سلامت تلفنی
    """
    site_url = request.build_absolute_uri('/')[:-1] if request else 'http://127.0.0.1:8000'
    subject = f'تایید ثبت نوبت مشاوره سلامت #{booking.id} | عطارخونه'

    context = {
        'booking': booking,
        'site_url': site_url,
    }

    try:
        html_content = render_to_string('emails/consultation_email.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.DEFAULT_FROM_EMAIL],  # اعلان به مدیر و پزشک مشاور
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"Consultation email notification sent for booking #{booking.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send consultation email: {e}")
        return False


def send_otp_verification_email(email, code, purpose='register', request=None):
    """
    ارسال کد تایید ۵ رقمی احراز هویت (OTP) به نشانی رایانامه با سرور رسمی جیمیل
    """
    if not email:
        return False

    site_url = request.build_absolute_uri('/')[:-1] if request else 'http://127.0.0.1:8001'
    purpose_titles = {
        'register': 'کد تایید فعال‌سازی و تکمیل ثبت‌نام',
        'login': 'کد یکبار مصرف ورود به سامانه',
        'reset': 'کد تایید بازیابی گذرواژه',
    }
    purpose_title = purpose_titles.get(purpose, 'کد تایید احراز هویت')
    subject = f'{code} : {purpose_title} | فروشگاه عطارخونه'

    context = {
        'email': email,
        'code': code,
        'purpose': purpose,
        'purpose_title': purpose_title,
        'site_url': site_url,
    }

    try:
        html_content = render_to_string('emails/otp_email.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"OTP verification email successfully sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email to {email}: {e}")
        return False

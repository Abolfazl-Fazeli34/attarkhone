from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """
    امکان احراز هویت و ورود همزمان با نام کاربری یا نشانی ایمیل
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if not username or not password:
            return None

        try:
            # جستجو بر اساس نام کاربری یا ایمیل (بدون حساسیت به حروف کوچک و بزرگ)
            user = UserModel.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).order_by('id').first()

            if user and user.check_password(password) and self.user_can_authenticate(user):
                return user
        except Exception:
            return None

        return None

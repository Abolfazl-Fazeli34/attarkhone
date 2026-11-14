from django.urls import path
from .views import (
    UserLoginView, UserRegisterView, UserLogoutView,
    UserProfileView, StaffDashboardView,
    PasswordResetRequestView, PasswordResetConfirmView,
    VerifyEmailOTPView, ResendOTPView, LoginWithOTPView
)
from .seller_views import (
    SellerDashboardView, SellerProductListView, SellerProductCreateView,
    SellerProductUpdateView, SellerProductDeleteView, SellerProductQRView,
    SellerOrdersView, SellerSettingsView, SellerApplyView, SellerProductToggleStockView
)

app_name = 'accounts'

urlpatterns = [
    # احراز هویت سنتی و OTP ایمیل
    path('login/', UserLoginView.as_view(), name='login'),
    path('login/otp/', LoginWithOTPView.as_view(), name='login_otp'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailOTPView.as_view(), name='verify_email'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    # نمایه و داشبورد کاربری
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('orders/', UserProfileView.as_view(), name='orders'),
    path('staff-dashboard/', StaffDashboardView.as_view(), name='staff_dashboard'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # پنل اختصاصی فروشندگان و مزارع گیاهان دارویی
    path('seller/apply/', SellerApplyView.as_view(), name='seller_apply'),
    path('seller/dashboard/', SellerDashboardView.as_view(), name='seller_dashboard'),
    path('seller/products/', SellerProductListView.as_view(), name='seller_products'),
    path('seller/products/add/', SellerProductCreateView.as_view(), name='seller_product_add'),
    path('seller/products/<int:product_id>/edit/', SellerProductUpdateView.as_view(), name='seller_product_edit'),
    path('seller/products/<int:product_id>/toggle-stock/', SellerProductToggleStockView.as_view(), name='seller_product_toggle_stock'),
    path('seller/products/<int:product_id>/delete/', SellerProductDeleteView.as_view(), name='seller_product_delete'),
    path('seller/products/<int:product_id>/qr/', SellerProductQRView.as_view(), name='seller_product_qr'),
    path('seller/orders/', SellerOrdersView.as_view(), name='seller_orders'),
    path('seller/settings/', SellerSettingsView.as_view(), name='seller_settings'),
]

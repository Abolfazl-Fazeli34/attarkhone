from django.urls import path
from .views import (
    CartView, AddToCartView, RemoveFromCartView,
    ApplyCouponView, RemoveCouponView,
    CheckoutView, MockPaymentGatewayView,
    BankReceiptView, OrderInvoiceView, OrderTrackingView
)

app_name = 'orders'

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/apply-coupon/', ApplyCouponView.as_view(), name='apply_coupon'),
    path('cart/remove-coupon/', RemoveCouponView.as_view(), name='remove_coupon'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/<str:tracking_code>/', MockPaymentGatewayView.as_view(), name='mock_gateway'),
    path('receipt/<str:tracking_code>/', BankReceiptView.as_view(), name='bank_receipt'),
    path('invoice/<str:tracking_code>/', OrderInvoiceView.as_view(), name='invoice'),
    path('tracking/', OrderTrackingView.as_view(), name='tracking'),
]

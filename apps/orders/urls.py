from django.urls import path
from .views import (
    CartView, AddToCartView, RemoveFromCartView,
    AddToCartAjaxView, UpdateQuantityAjaxView, RemoveItemAjaxView,
    ApplyCouponView, RemoveCouponView,
    CheckoutView, MockPaymentGatewayView,
    ZarinpalGatewayView, ZarinpalCallbackView,
    BankReceiptView, OrderInvoiceView, OrderTrackingView
)

app_name = 'orders'

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/add-ajax/<int:product_id>/', AddToCartAjaxView.as_view(), name='add_to_cart_ajax'),
    path('cart/update-ajax/<int:item_id>/', UpdateQuantityAjaxView.as_view(), name='update_quantity_ajax'),
    path('cart/remove-ajax/<int:item_id>/', RemoveItemAjaxView.as_view(), name='remove_item_ajax'),
    path('cart/remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/apply-coupon/', ApplyCouponView.as_view(), name='apply_coupon'),
    path('cart/remove-coupon/', RemoveCouponView.as_view(), name='remove_coupon'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/zarinpal/gateway/<str:tracking_code>/', ZarinpalGatewayView.as_view(), name='zarinpal_gateway_view'),
    path('payment/zarinpal/callback/<str:tracking_code>/', ZarinpalCallbackView.as_view(), name='zarinpal_callback'),
    path('payment/<str:tracking_code>/', MockPaymentGatewayView.as_view(), name='mock_gateway'),
    path('receipt/<str:tracking_code>/', BankReceiptView.as_view(), name='bank_receipt'),
    path('invoice/<str:tracking_code>/', OrderInvoiceView.as_view(), name='invoice'),
    path('tracking/', OrderTrackingView.as_view(), name='tracking'),
]

from django.urls import path
from .views import ProductListView, ProductDetailView, WishlistView, WishlistToggleView, AddProductReviewView

app_name = 'catalog'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', WishlistToggleView.as_view(), name='wishlist_toggle'),
    path('category/<slug:category_slug>/', ProductListView.as_view(), name='product_list_by_category'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:product_id>/review/', AddProductReviewView.as_view(), name='add_review'),
]

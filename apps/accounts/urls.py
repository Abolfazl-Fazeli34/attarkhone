from django.urls import path
from .views import (
    UserLoginView, UserRegisterView, UserLogoutView,
    UserProfileView, StaffDashboardView
)

app_name = 'accounts'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('orders/', UserProfileView.as_view(), name='orders'),
    path('staff-dashboard/', StaffDashboardView.as_view(), name='staff_dashboard'),
]

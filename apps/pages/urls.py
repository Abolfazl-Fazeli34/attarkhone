from django.urls import path
from .views import PageDetailView, ContactUsView

app_name = 'pages'

urlpatterns = [
    path('contact-us/', ContactUsView.as_view(), name='contact_us'),
    path('<slug:slug>/', PageDetailView.as_view(), name='page_detail'),
]

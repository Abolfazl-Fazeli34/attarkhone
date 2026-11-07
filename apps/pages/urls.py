from django.urls import path
from .views import PageDetailView, ContactUsView, ArticleListView, ArticleDetailView

app_name = 'pages'

urlpatterns = [
    path('articles/', ArticleListView.as_view(), name='article_list'),
    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    path('contact-us/', ContactUsView.as_view(), name='contact_us'),
    path('<slug:slug>/', PageDetailView.as_view(), name='page_detail'),
]

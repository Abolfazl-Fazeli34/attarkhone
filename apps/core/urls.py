from django.urls import path
from .views import HomeView, HealthCheckView, WorkshopsGuideView, robots_txt

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('health-check/', HealthCheckView.as_view(), name='health_check'),
    path('workshops-guide/', WorkshopsGuideView.as_view(), name='workshops_guide'),
    path('robots.txt', robots_txt, name='robots_txt'),
]

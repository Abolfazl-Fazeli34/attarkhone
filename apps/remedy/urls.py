from django.urls import path
from .views import RemedyWizardView, DrugCheckAPIView, AddPackageToCartView

app_name = 'remedy'

urlpatterns = [
    path('', RemedyWizardView.as_view(), name='wizard_index'),
    path('wizard/', RemedyWizardView.as_view(), name='wizard'),
    path('api/check-drug/', DrugCheckAPIView.as_view(), name='check_drug'),
    path('package/add/<int:package_id>/', AddPackageToCartView.as_view(), name='add_package_to_cart'),
]

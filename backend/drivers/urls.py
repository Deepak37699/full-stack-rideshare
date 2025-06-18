from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'drivers', views.DriverViewSet)
router.register(r'documents', views.DriverDocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.DriverRegistrationView.as_view(), name='driver_register'),
    path('status/', views.DriverStatusView.as_view(), name='driver_status'),
    path('earnings/', views.DriverEarningsView.as_view(), name='driver_earnings'),
    path('available-rides/', views.AvailableRidesView.as_view(), name='available_rides'),
]

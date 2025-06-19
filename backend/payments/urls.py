from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'payments', views.PaymentViewSet)
router.register(r'payment-methods', views.PaymentMethodViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
